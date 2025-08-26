import os, unittest, importlib.util, sys, json, pathlib

class SanityTests(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(os.path.exists('README.md'))

    def test_package_version(self):
        import jetport
        self.assertTrue(hasattr(jetport, '__version__'))
        self.assertIsInstance(jetport.__version__, str)

    def test_example_app_callable(self):
        # ensure example_app.py defines 'app' callable
        import example_app
        self.assertTrue(hasattr(example_app, 'app'))
        self.assertTrue(callable(example_app.app))

    def test_inspector_template(self):
        from jetport import inspector
        html = inspector._index_html()
        self.assertIn('<title>JetPort Inspector</title>', html)

if __name__ == '__main__':
    unittest.main()
