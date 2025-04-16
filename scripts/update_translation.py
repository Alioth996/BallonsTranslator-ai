import os
import os.path as osp
from glob import glob

from qtpy.QtCore import QLocale
SYSLANG = QLocale.system().name()

if __name__ == '__main__':
    program_dir = osp.dirname(osp.dirname(osp.abspath(__file__)))
    translate_dir = osp.dirname(osp.abspath(__file__)).replace('scripts', 'translate')
    translate_path = osp.join(translate_dir, SYSLANG+'.ts')

    # 处理路径中的空格问题
    py_files = glob(osp.join(program_dir, 'ui/*.py'))
    py_files_quoted = [f'"{f}"' for f in py_files]

    cmd = 'pylupdate5 -verbose '+ \
          ' '.join(py_files_quoted) + \
          ' -ts "' + translate_path + '"'

    print('target language: ', SYSLANG)
    os.system(cmd)
    print(f'Saved to {translate_path}')