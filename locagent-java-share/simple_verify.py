#!/usr/bin/env python3
from dependency_graph.build_graph import build_graph

def verify_graph_accuracy():
    """验证图的准确性"""
    print("=== LocAgent 图准确性验证 ===")
    
    # 构建图
    graph = build_graph('test_data')
    
    print(f"\n📊 图统计:")
    print(f"   节点数: {graph.number_of_nodes()}")
    print(f"   边数: {graph.number_of_edges()}")
    
    # 验证文件检测
    print(f"\n📁 文件检测验证:")
    files = [n for n, d in graph.nodes(data=True) if d.get('type') == 'file']
    print(f"   检测到的文件: {files}")
    expected_files = ['ComplexTest.java', 'Calculator.java']
    print(f"   期望的文件: {expected_files}")
    
    # 验证类检测
    print(f"\n🏗️  类检测验证:")
    classes = [n.split('.')[-1] for n, d in graph.nodes(data=True) if d.get('type') == 'class' and 'external' not in n]
    print(f"   检测到的类: {classes}")
    expected_classes = ['ComplexTest', 'AbstractBase', 'DataProcessorImpl', 'ExternalService', 'Calculator', 'AdvancedCalculator']
    print(f"   期望的类: {expected_classes}")
    
    # 验证继承关系
    print(f"\n🧬 继承关系验证:")
    inheritance = [(u.split('.')[-1], v.split('.')[-1]) for u, v, d in graph.edges(data=True) if d['type'] == 'inherits']
    print(f"   检测到的继承: {inheritance[:10]}")  # 显示前10个
    expected_inheritance = [
        ('ComplexTest', 'AbstractBase'),
        ('ComplexTest', 'DataProcessor'),
        ('AdvancedCalculator', 'Calculator'),
        ('AdvancedCalculator', 'MathOperation')
    ]
    print(f"   期望的继承: {expected_inheritance}")
    
    # 验证方法调用
    print(f"\n📞 方法调用验证:")
    invokes = [(u.split('.')[-1], v.split('.')[-1]) for u, v, d in graph.edges(data=True) if d['type'] == 'invokes']
    print(f"   检测到的调用: {invokes[:10]}")  # 显示前10个
    expected_calls = [
        ('perform', 'add'),
        ('perform', 'subtract'),
        ('perform', 'multiply'),
        ('perform', 'divide')
    ]
    print(f"   期望的调用: {expected_calls}")
    
    # 验证导入关系
    print(f"\n📦 导入关系验证:")
    imports = [(u, v) for u, v, d in graph.edges(data=True) if d['type'] == 'imports']
    print(f"   检测到的导入: {imports}")
    expected_imports = [
        ('ComplexTest.java', 'external:java.util'),
        ('ComplexTest.java', 'external:java.io'),
        ('Calculator.java', 'external:java.util.List'),
        ('Calculator.java', 'external:java.util.ArrayList')
    ]
    print(f"   期望的导入: {expected_imports}")
    
    # 计算准确率
    print(f"\n✅ 准确性评估:")
    
    # 文件检测准确率
    file_accuracy = len(set([f.split('/')[-1] for f in files]) & set(expected_files)) / len(expected_files)
    print(f"   文件检测准确率: {file_accuracy:.2%}")
    
    # 类检测准确率
    class_accuracy = len(set(classes) & set(expected_classes)) / len(expected_classes)
    print(f"   类检测准确率: {class_accuracy:.2%}")
    
    # 继承关系准确率
    inheritance_accuracy = len(set(inheritance) & set(expected_inheritance)) / len(expected_inheritance)
    print(f"   继承关系准确率: {inheritance_accuracy:.2%}")
    
    # 方法调用准确率
    call_accuracy = len(set(invokes) & set(expected_calls)) / len(expected_calls)
    print(f"   方法调用准确率: {call_accuracy:.2%}")
    
    # 导入关系准确率
    import_accuracy = len(set(imports) & set(expected_imports)) / len(expected_imports)
    print(f"   导入关系准确率: {import_accuracy:.2%}")
    
    # 总体准确率
    overall_accuracy = (file_accuracy + class_accuracy + inheritance_accuracy + call_accuracy + import_accuracy) / 5
    print(f"   总体准确率: {overall_accuracy:.2%}")

if __name__ == "__main__":
    verify_graph_accuracy() 