from path_init import SAMPLE_DIR
import sys
import os.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(TEST_DIR), 'src')
sys.path.append(SRC_DIR)
