import os
from pathlib import Path
import shutil
import subprocess
import unittest


class InteractiveDetailChartsTests(unittest.TestCase):
    def test_task3_denominators_filters_colors_and_contrasts(self):
        self.run_journey('task3_clarity.cjs')

    def test_task3_metadata_filters_and_cross_analysis_journey(self):
        self.run_journey('task3_facets.cjs')

    def test_paper_task3_type_analysis_journey(self):
        self.run_journey('paper_task3_types.cjs')

    def test_task3_type_analysis_journey(self):
        self.run_journey('task3_types.cjs')

    def test_per_task_context_and_search_recovery(self):
        self.run_journey('task_context.cjs')

    def test_observed_difference_semantics(self):
        self.run_journey('observed_differences.cjs')

    def test_first_user_chart_clarity_and_design(self):
        self.run_journey('chart_clarity_design.cjs')

    def test_legend_order_shared_rows_and_denominator_regressions(self):
        self.run_journey('chart_usability.cjs')

    def test_detail_to_compare_condition_handoff(self):
        self.run_journey('chart_handoff.cjs')

    def run_journey(self, script):
        node = os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        subprocess.run([node, 'tests/' + script], cwd=Path(__file__).resolve().parents[1], check=True, timeout=30)

    def test_shipped_renderer_and_exact_adapters(self):
        node = os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        subprocess.run([node, 'tests/detail_charts.cjs'], cwd=Path(__file__).resolve().parents[1], check=True, timeout=30)

    def test_assets_are_served_and_summary_remains_numerical(self):
        from fastapi.testclient import TestClient
        from koevd_eval.spaces import create_app
        import test_spaces
        f = test_spaces.SpaceServiceTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        with TestClient(create_app(f.service, origins=['http://localhost']), base_url='http://localhost') as client:
            for name, media in [('detail_charts.js', 'javascript'), ('detail_charts.css', 'css')]:
                response = client.get('/assets/' + name)
                self.assertEqual(response.status_code, 200)
                self.assertIn(media, response.headers['content-type'])
