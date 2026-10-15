"""Numerical export agreement, permission races and untrusted metadata."""
from copy import deepcopy
import csv
import io
import json
import unittest
from unittest.mock import patch

import test_public_leaderboard as fixture
import test_public_comparison as pair_fixture
import test_submission_web as web_fixture
from koevd_eval.public_exports import make_export,checked_export,numerical_rows
from koevd_eval.storage import StorageError


class PublicExportTests(unittest.TestCase):
    setUp=fixture.PublicLeaderboardTests.setUp
    key=fixture.PublicLeaderboardTests.key
    action=fixture.PublicLeaderboardTests.action
    create=fixture.PublicLeaderboardTests.create
    publish=fixture.PublicLeaderboardTests.publish
    publish_state=fixture.PublicLeaderboardTests.publish_state
    other_document=fixture.PublicLeaderboardTests.other_document
    pair=pair_fixture.PublicComparisonTests.pair

    def test_five_exports_preserve_exact_engine_numbers_and_omit_originals(self):
        left,right,_=self.pair()
        for value in (self.service.public_profile(left['id']),self.service.public_comparison(left['id'],right['id'])):
            expected=list(numerical_rows(value))
            self.assertTrue(all('submission_revision' in row and 'model_revision' in row for row in expected if row['kind']!='paired_difference'))
            self.assertFalse(any('revision' in row for row in expected))
            self.assertFalse(any(row['kind']=='paired_difference' and row['task']==4 for row in expected))
            for fmt in ('json','jsonl','csv','markdown','html'):
                raw,media,name=make_export(value,fmt)
                for private in ('fixture response','"sample_ids"','"cases"','private review note','"owner"','"request_id"'):
                    self.assertNotIn(private,raw.decode())
                self.assertTrue(name.startswith('koevd-public-'))
                if fmt=='json':self.assertEqual(json.loads(raw),value)
                if fmt=='jsonl':self.assertEqual([{k:v for k,v in json.loads(line).items() if k!='format'} for line in raw.splitlines()],expected)
                if fmt=='csv':
                    rows=list(csv.DictReader(io.StringIO(raw.decode())))
                    self.assertEqual(len(rows),len(expected))
                    for given,row in zip(expected,rows):
                        for field in ('value','numerator','denominator','coverage_numerator','coverage_denominator'):
                            number=given.get(field)
                            self.assertEqual(row[field],'' if number is None else str(number))

    def test_untrusted_names_are_literal_and_csv_formulas_are_escaped(self):
        state=self.publish();value=self.service.public_profile(state['id'])
        attack='=HYPERLINK("https://invalid.example", "click") <img src=x onerror=alert(1)> ![x](https://invalid.example)'
        value['display']['display_name']=attack
        raw,_,_=make_export(value,'csv')
        self.assertTrue(next(csv.DictReader(io.StringIO(raw.decode())))['display_name'].startswith("'="))
        raw,_,_=make_export(value,'html');text=raw.decode()
        for active in ('<script','<img',' onerror="','href="https://invalid.example'):
            self.assertNotIn(active,text)
        self.assertIn('&lt;img',text);self.assertIn('default-src',text)
        raw,_,_=make_export(value,'markdown')
        self.assertNotIn('![x](https://',raw.decode())
        self.assertIn('\\!\\[x\\]',raw.decode())

    def test_render_withdrawal_or_changed_metadata_discards_download(self):
        state=self.publish();self.service.public_profile(state['id'])
        original=make_export
        def withdraw(value,fmt):
            result=original(value,fmt);self.action(state,'withdraw');return result
        with patch('koevd_eval.public_exports.make_export',side_effect=withdraw):
            with self.assertRaises(StorageError) as caught:
                checked_export(lambda:self.service.public_profile(state['id']),'html')
        self.assertEqual(caught.exception.code,'not_found')
        other=self.publish(self.other_document())
        def rename(value,fmt):
            result=original(value,fmt)
            self.service.update_display(self.author,other['id'],display_name='changed',description='',
                expected_version=other['version'],key=self.key());return result
        with patch('koevd_eval.public_exports.make_export',side_effect=rename):
            with self.assertRaises(StorageError) as caught:
                checked_export(lambda:self.service.public_profile(other['id']),'csv')
        self.assertEqual(caught.exception.code,'publication_changed')

    def test_projection_does_not_export_accidental_private_fields_and_capacity_is_explicit(self):
        value=self.service.public_profile(self.publish()['id'])
        injected=deepcopy(value);injected['owner']='NEVER_PUBLIC';injected['analysis']['cases']=[{'response':'NEVER_PUBLIC'}]
        self.assertNotIn('NEVER_PUBLIC',make_export(injected,'json')[0].decode())
        with patch('koevd_eval.public_exports.MAX_EXPORT_BYTES',1):
            with self.assertRaises(StorageError) as error:make_export(value,'html')
        self.assertEqual(error.exception.code,'export_capacity')
        with self.assertRaises(StorageError) as error:make_export(value,'pickle')
        self.assertEqual(error.exception.code,'export_format')

    def test_withdrawal_during_paired_export_rechecks_both_publications(self):
        left,right,_=self.pair();self.service.public_comparison(left['id'],right['id'])
        original=make_export
        def during(value,fmt):
            result=original(value,fmt);self.action(right,'withdraw');return result
        with patch('koevd_eval.public_exports.make_export',side_effect=during):
            with self.assertRaises(StorageError) as caught:
                checked_export(lambda:self.service.public_comparison(left['id'],right['id']),'json')
        self.assertEqual(caught.exception.code,'not_found')


class PublicExportHTTPTests(unittest.TestCase):
    setUp=web_fixture.SubmissionHTTPTests.setUp
    setUpFixture=web_fixture.SubmissionHTTPTests.setUpFixture
    write=web_fixture.SubmissionHTTPTests.write
    sha=web_fixture.SubmissionHTTPTests.sha
    upload=web_fixture.SubmissionHTTPTests.upload
    login=web_fixture.SubmissionHTTPTests.login
    headers=web_fixture.SubmissionHTTPTests.headers
    action=web_fixture.SubmissionHTTPTests.action
    create=web_fixture.SubmissionHTTPTests.create
    publish=web_fixture.SubmissionHTTPTests.publish

    def test_anonymous_pair_download_matches_current_comparison_and_denies_withdrawal(self):
        from koevd_eval.results import _seal
        left,_=self.publish();document=deepcopy(self.document)
        document['run']['model']['id']='SYNTHETIC-other-export'
        document=_seal({k:v for k,v in document.items() if k!='content_sha256'})
        entry=self.upload(document)
        response=self.author.post('/api/submissions',headers=self.headers(self.author),json={
            'upload_id':entry['id'],'key':'other-export'})
        self.assertEqual(response.status_code,201,response.text);right=response.json()
        self.submissions.allow_self_reported_summaries=True
        response=self.action(self.author,right,'publish_summary',consent={
            'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC export permission'})
        self.assertEqual(response.status_code,200,response.text);right=response.json()
        params={'left':left['id'],'right':right['id']}
        expected=self.other.get('/api/public/compare',params=params).json()
        for fmt in ('json','jsonl','csv','markdown','html'):
            response=self.other.get('/api/public/compare/download',params={**params,'format':fmt})
            self.assertEqual(response.status_code,200,response.text)
            self.assertNotIn('fixture response',response.text)
            if fmt=='json':self.assertEqual(response.json(),expected)
        response=self.action(self.author,right,'withdraw');self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.other.get('/api/public/compare/download',params=params).status_code,404)

    def test_anonymous_download_is_a_current_numerical_attachment_not_private_original(self):
        state,_=self.publish()
        url='/api/public/submissions/'+state['id']+'/profile/download'
        expected=self.other.get('/api/public/submissions/'+state['id']+'/profile').json()
        self.assertFalse(self.other.get('/api/identity').json()['signed_in'])
        for fmt in ('json','jsonl','csv','markdown','html'):
            response=self.other.get(url,params={'format':fmt});self.assertEqual(response.status_code,200,response.text)
            self.assertTrue(response.headers['content-disposition'].startswith('attachment;'))
            self.assertEqual(response.headers['cache-control'],'no-store')
            self.assertNotIn('fixture response',response.text)
            if fmt=='json':self.assertEqual(response.json(),expected)
        self.assertEqual(self.other.get('/api/public/submissions/'+state['id']+'/result').status_code,403)
        self.assertEqual(self.other.get(url,params={'format':'zip'}).status_code,400)
        self.assertEqual(self.other.get('/api/public/submissions/not-found/profile/download').status_code,404)
        response=self.action(self.author,state,'withdraw');self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.other.get(url).status_code,404)
