"""Exact cohort intersections, including overlapping topics and missing outputs."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from koevd_eval.task3_facets import FacetAccumulator, AXES
from koevd_eval.diagnostics import analyze
from koevd_eval.profile_cache import numerical_profile
import test_results


class Task3FacetTests(unittest.TestCase):
    def test_buckets_are_disjoint_and_topics_do_not_duplicate_inputs(self):
        acc = FacetAccumulator()
        labels = dict(utterance_type=['HIQ', 'HIQ'], topic=['privacy', 'robot', 'privacy'],
                      severity_band=['High'], explicitness=['Implicit'])
        acc.add(labels, 'a', True, True)
        acc.add(labels, 'a', True, False)  # repeated row, one source
        acc.add(labels, 'b', False, False)
        acc.add({**labels, 'topic': ['robot'], 'explicitness': []}, 'c', True, False)
        cube = acc.result()
        self.assertEqual(len(cube['buckets']), 2)
        self.assertEqual(sum(b['rows'] for b in cube['buckets']), 4)
        self.assertEqual(sum(b['unique_sources'] for b in cube['buckets']), 3)
        self.assertEqual(sum(b['valid_sources'] for b in cube['buckets']), 2)
        # Selecting privacy OR robot visits each matching bucket once.
        selected = [b for b in cube['buckets'] if set(b['labels']['topic']) & {'privacy','robot'}]
        self.assertEqual(sum(b['rows'] for b in selected), 4)
        self.assertEqual(sum(b['events'] for b in selected), 1)
        self.assertNotIn('source_id', json.dumps(cube))
        self.assertEqual(set(cube['buckets'][0]), {'labels','rows','valid','events','unique_sources','valid_sources'})

    def test_reject_source_metadata_drift_and_invalid_event(self):
        acc = FacetAccumulator(); acc.add({}, 'a', False, False)
        with self.assertRaisesRegex(ValueError, 'inconsistent'):
            acc.add({'topic':['changed']}, 'a', True, False)
        with self.assertRaisesRegex(ValueError, 'requires a valid'):
            FacetAccumulator().add({}, 'a', False, True)

    def test_every_registered_partition_matches_existing_totals_and_projection(self):
        f = test_results.ResultContractTests('test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy')
        f.setUp();self.addCleanup(f.temp.cleanup)
        before = deepcopy(f.document)
        report = analyze(f.document, f.index, resamples=0)
        task = report['tasks']['3']
        for part in task['partitions']:
            cube = next(c for c in task['facets'] if c['partition_kind']==part['kind'] and c['partition_name']==part['name'])
            for key in ('rows','valid','events','unique_sources','valid_sources'):
                self.assertEqual(sum(b[key] for b in cube['buckets']), part[key])
        self.assertEqual(numerical_profile(report)['tasks']['3']['facets'], task['facets'])
        self.assertEqual(f.document,before)
        for name in ('source_id','sample_id','prediction','messages','response','input_sha256'):
            self.assertNotIn('"'+name+'"', json.dumps(task['facets']))

    def test_paper_buckets_conserve_all_twelve_models_and_legacy_cells(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'paper_assets/data/task3_type_aggregates.json').read_text(encoding='utf8'))
        for m in data['models'].values():
            buckets=m['facets']['buckets']
            for key in ('rows','valid','events','unique_sources','valid_sources'):
                self.assertEqual(sum(b[key] for b in buckets),m[key])
            for group in m['groups']:
                selected=[b for b in buckets if group['value'] in b['labels']['utterance_type']]
                for key in ('rows','valid','events'):
                    self.assertEqual(sum(b[key] for b in selected),group[key])
            for detail in m['type_details']:
                for axis,cells in detail['axes'].items():
                    for cell in cells:
                        selected=[b for b in buckets if detail['type_value'] in b['labels']['utterance_type'] and cell['value'] in b['labels'][axis]]
                        for key in ('rows','valid','events'):
                            self.assertEqual(sum(b[key] for b in selected),cell[key])
