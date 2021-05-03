import os
from unittest import TestCase

from octue import Runner

from app import REPOSITORY_ROOT


class TestXFoil(TestCase):

    def get_xfoil_case_path(self, xfoil_case):
        """Sets XFOIL with the case"""
        return os.path.join(REPOSITORY_ROOT, "tests", "xfoil", "cases", xfoil_case)

    def test_call(self):
        """Test that xfoil runs NACA0012 analysis and that results are consistent with compiled version from NASA
        website.
        """
        case_path = self.get_xfoil_case_path("naca0012")

        runner = Runner(
            app_src=REPOSITORY_ROOT,
            twine=os.path.join(REPOSITORY_ROOT, "twine.json"),
            configuration_values=os.path.join(case_path, "data", "configuration", "values.json")
        )

        analysis = runner.run(
            input_values=os.path.join(case_path, "data", "input", "values.json"),
            input_manifest=os.path.join(case_path, "data", "input", "manifest.json")
        )

        analysis.finalise(output_dir=os.path.join(case_path, "data", "output"))