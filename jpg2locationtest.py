import unittest
import jpg2location
#try:
#    from StringIO import StringIO ## for Python 2
#except ImportError:
from io import StringIO ## for Python 3
import sys


# "args": ["testfiles/file*.jpg","testfiles/sunrset_philippines.jpg","testfiles/subdir/flooding.jpg","testfiles/mason-on-mckinney-apt.jpg","testfiles/file3.jpg"]

class JPG2LocationTest(unittest.TestCase):
    def test_init(self):
        # Initialization of configuration settings and logging
        config = jpg2location.load_config()
        validator = jpg2location.Jpg2Location( config )
        self.assertEqual(config,validator.config)
        self.assertIsNotNone(validator.location_cache)

    def test_files(self):
        try:
            captured_output = StringIO()
            sys.stdout = captured_output

            # Initialization of configuration settings and logging
            config = jpg2location.load_config()
            validator = jpg2location.Jpg2Location( config )
            pathnames = ["testfiles/file*.jpg","testfiles/sunrset_philippines.jpg","testfiles/subdir/flooding.jpg","testfiles/mason-on-mckinney-apt.jpg","testfiles/file3.jpg"]
            validator.print_multiple_files_and_postalcodes( pathnames=pathnames )

            sys.stdout = sys.__stdout__

            console_output = captured_output.getvalue()
            self.assertTrue( '75204' in console_output )
            self.assertTrue( '77060' in console_output )

            self.assertTrue( config['tags']['no_geocode'] in console_output )
            self.assertTrue( config['tags']['not_jpeg'] in console_output )
            self.assertTrue( config['tags']['file_not_found'] in console_output )            

            self.assertTrue( config['tags']['internal_error'] not in console_output )            

        finally:
            sys.stdout = sys.__stdout__
            validator = None



if __name__ == "__main__":
    unittest.main()