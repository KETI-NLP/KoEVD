"""Lossless HTTP compression with independent wire and expanded-byte bounds."""
import re
import zlib

from .space_service import ServiceError


async def receive_result(request, path, *, limit, encoding, expected_length=None):
    """Write one JSON body; reject damaged, concatenated or oversized gzip."""
    if encoding not in ('identity','gzip'):
        raise ServiceError('content_encoding','Use an uncompressed or gzip JSON body.',415)
    decoder=zlib.decompressobj(16+zlib.MAX_WBITS) if encoding=='gzip' else None
    wire=expanded=0
    with path.open('xb') as stream:
        async for chunk in request.stream():
            wire+=len(chunk)
            if wire>limit:raise ServiceError('upload_size','Result transfer exceeds the upload limit.',413)
            if decoder is None:
                expanded+=len(chunk)
                if expanded>limit:raise ServiceError('upload_size','Result exceeds the upload limit.',413)
                stream.write(chunk)
                continue
            pending=chunk
            while pending:
                try:decoded=decoder.decompress(pending,min(65536,limit-expanded+1))
                except zlib.error:
                    raise ServiceError('invalid_gzip','Invalid gzip JSON transfer.',422) from None
                expanded+=len(decoded)
                if expanded>limit:raise ServiceError('upload_size','Expanded result exceeds the upload limit.',413)
                stream.write(decoded)
                if decoder.unused_data:
                    raise ServiceError('invalid_gzip','Use exactly one complete gzip member without trailing data.',422)
                pending=decoder.unconsumed_tail
    if expected_length is not None and wire!=expected_length:
        raise ServiceError('length','Body length differs from Content-Length.')
    if decoder is not None and not decoder.eof:
        raise ServiceError('invalid_gzip','Incomplete gzip JSON transfer.',422)


class ResultCompressionMiddleware:
    """Compress result/report bodies after their existing access checks.

    Identity/session endpoints and their authentication fields are excluded.
    Clients without gzip support receive the original uncompressed bytes.
    """
    def __init__(self, app):
        from starlette.middleware.gzip import GZipMiddleware
        self.app=app
        self.compressed=GZipMiddleware(app,minimum_size=1024,compresslevel=5)

    async def __call__(self, scope, receive, send):
        path=scope.get('path','')
        ranged=any(name.lower()==b'range' for name,_ in scope.get('headers',[]))
        eligible=(scope['type']=='http' and scope.get('method')=='GET' and not ranged and (
            path in ('/api/public/submissions','/api/public/leaderboard',
                     '/api/public/compare','/api/public/compare/download')
            or re.fullmatch(r'/api/public/submissions/[A-Za-z0-9_-]+(?:/profile(?:/download)?)?',path)
            or re.fullmatch(r'/api/submissions/[A-Za-z0-9_-]+/result',path)
            or re.fullmatch(r'/api/reports/[A-Za-z0-9_-]+/(?:html|profile|cases|csv|markdown)',path)))
        await (self.compressed if eligible else self.app)(scope,receive,send)
