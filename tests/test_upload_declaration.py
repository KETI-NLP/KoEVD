"""Private metadata confirmation without exposing another session or raw text."""
import json
import unittest
import test_spaces as fixtures
from koevd_eval.space_service import ServiceError


class DeclarationTests(unittest.TestCase):
    setUp=fixtures.SpaceServiceTests.setUp
    upload=fixtures.SpaceServiceTests.upload
    write=fixtures.SpaceServiceTests.write
    sha=fixtures.SpaceServiceTests.sha

    def test_declaration_matches_original_without_raw_output_or_fake_verification(self):
        entry=self.upload();value=self.service.upload_declaration(self.token,entry['id'])
        self.assertEqual(value['model'],self.document['run']['model'])
        self.assertEqual(value['generation'],self.document['run']['generation'])
        self.assertEqual(value['measurements'],self.document['run']['measurements'])
        self.assertEqual(value['record_counts'],{'1':1,'2':4,'3':2,'4':2,'5':3})
        self.assertEqual(value['verification'],'structurally_validated_user_reported')
        self.assertIsNone(value['model']['revision'])
        for raw in ('fixture response','"records"','"response"','internal-secret-endpoint','private/path'):
            self.assertNotIn(raw,json.dumps(value))
        self.assertFalse(self.service.sessions[next(iter(self.service.sessions))].busy)

    def test_other_session_and_expired_session_cannot_read_declaration(self):
        entry=self.upload();other,_=self.service.create_session()
        with self.assertRaises(ServiceError) as error:self.service.upload_declaration(other,entry['id'])
        self.assertEqual(error.exception.status,404)
        self.clock[0]=self.service.limits.ttl_seconds+1
        with self.assertRaises(ServiceError) as error:self.service.upload_declaration(self.token,entry['id'])
        self.assertEqual(error.exception.status,401)

    def test_changed_bytes_are_rejected_and_busy_flag_released(self):
        entry=self.upload();session=self.service.sessions[next(iter(self.service.sessions))]
        path=session.uploads[entry['id']]['path'];path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaises(ServiceError) as error:self.service.upload_declaration(self.token,entry['id'])
        self.assertEqual(error.exception.code,'upload_integrity')
        self.assertFalse(session.busy)


class DeclarationHTTPTests(unittest.TestCase):
    setUp=fixtures.SpaceHTTPTests.setUp
    write=fixtures.SpaceHTTPTests.write
    sha=fixtures.SpaceHTTPTests.sha

    def test_http_uses_analysis_session_access_without_identity_or_score_inputs(self):
        response=self.client.post('/api/uploads',content=json.dumps(self.document),headers={**self.headers,'Content-Type':'application/json'})
        self.assertEqual(response.status_code,201,response.text)
        url='/api/uploads/'+response.json()['id']+'/declaration'
        value=self.client.get(url,headers=self.headers)
        self.assertEqual(value.status_code,200,value.text)
        self.assertEqual(value.json()['model'],self.document['run']['model'])
        self.assertEqual(self.client.get(url).status_code,401)
        token,_=self.service.create_session()
        self.assertEqual(self.client.get(url,headers={'Authorization':'Bearer '+token}).status_code,404)
