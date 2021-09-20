# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'
__date__ = '2021-09-20 21:41:24'

import os
import unittest


def run_all_tests(start_dir: str):
    """
    用于按方法运行指定目录下的所有测试文件
    :return:
    """
    runner = unittest.TextTestRunner(verbosity=2)
    tests = unittest.defaultTestLoader.discover(start_dir=start_dir, pattern='test_*.py')
    runner.run(test=tests)


def run_all_test_class(start_dir: str):
    """
        用于按类运行指定目录下的所有测试文件

        ①. 遍历指定路径下的测试文件(以 'test' 开头，以 '.py' 结尾)
        ②. 将文件转化为ast树
        ③. 获取树中的类
        ④. 过滤出以 'Test' 开头的类
        ⑤. 加载类
        ⑥. 执行测试类
    """

    import ast  # https://www.codeleading.com/article/65524397149/
    import importlib

    runner = unittest.TextTestRunner(verbosity=2)
    tests = 0
    errors = 0
    failures = 0
    for root, sub_dirs, files in os.walk(top=start_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filename = os.path.join(root, file)
                with open(filename, 'r') as f:
                    tree = ast.parse(f.read())
                    cls_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    for cls_name in cls_names:
                        if cls_name.startswith('Test'):
                            module_name = os.path.splitext(file)[0]
                            module = importlib.import_module(module_name)
                            cls = getattr(module, cls_name)
                            suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
                            result = runner.run(test=suite)
                            # 统计
                            tests += result.testsRun
                            errors += len(result.errors)
                            failures += len(result.failures)
    print(f'tests: {tests}, errors: {errors}, failures: {failures}')
