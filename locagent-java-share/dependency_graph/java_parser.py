"""
Java parser module for LocAgent using tree-sitter.
This module provides Java code parsing capabilities with high fidelity.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Try to import tree-sitter first
try:
    from tree_sitter import Parser, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not available, falling back to javalang")

# Try to import javalang as fallback
try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False
    print("Warning: javalang not available")

# Add the scripts directory to the path to import tree_sitter_languages
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from tree_sitter_languages import get_language, JAVA_LANGUAGE
except ImportError as e:
    print(f"Warning: Could not import tree-sitter languages: {e}")
    JAVA_LANGUAGE = None

# Node types for Java
NODE_TYPE_DIRECTORY = 'directory'
NODE_TYPE_FILE = 'file'
NODE_TYPE_CLASS = 'class'
NODE_TYPE_FUNCTION = 'function'
NODE_TYPE_INTERFACE = 'interface'
NODE_TYPE_ENUM = 'enum'

class JavaCodeAnalyzer:
    """Java code analyzer using tree-sitter or javalang."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.nodes = []
        self.node_name_stack = []
        self.node_type_stack = []
        self.package_name = ""
        
        # Try tree-sitter first
        if TREE_SITTER_AVAILABLE and JAVA_LANGUAGE is not None:
            self.parser = Parser()
            self.parser.set_language(JAVA_LANGUAGE)
            self.use_tree_sitter = True
        elif JAVALANG_AVAILABLE:
            self.use_tree_sitter = False
        else:
            raise RuntimeError("No Java parser available. Please install tree-sitter or javalang.")
    
    def parse_file(self) -> List[Dict[str, Any]]:
        """Parse a Java file and extract classes, interfaces, enums, and methods."""
        with open(self.filename, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        if self.use_tree_sitter:
            return self._parse_with_tree_sitter(source_code)
        else:
            return self._parse_with_javalang(source_code)
    
    def _parse_with_tree_sitter(self, source_code: str) -> List[Dict[str, Any]]:
        """Parse using tree-sitter."""
        tree = self.parser.parse(bytes(source_code, 'utf8'))
        root_node = tree.root_node
        
        # Extract package declaration
        self._extract_package(root_node, source_code)
        
        # Visit all nodes
        self._visit_node(root_node, source_code)
        
        return self.nodes
    
    def _parse_with_javalang(self, source_code: str) -> List[Dict[str, Any]]:
        """Parse using javalang."""
        try:
            tree = javalang.parse.parse(source_code)
            if tree.package:
                self.package_name = tree.package.name
            # 只遍历顶层类型，避免重复遍历
            for type_decl in tree.types:
                if isinstance(type_decl, javalang.tree.ClassDeclaration):
                    self._visit_javalang_class(type_decl, source_code)
                elif isinstance(type_decl, javalang.tree.InterfaceDeclaration):
                    self._visit_javalang_interface(type_decl, source_code)
                elif isinstance(type_decl, javalang.tree.EnumDeclaration):
                    self._visit_javalang_enum(type_decl, source_code)
            return self.nodes
        except Exception as e:
            print(f"Error parsing with javalang: {e}")
            return []
    
    def _extract_package(self, root_node: Node, source_code: str):
        """Extract package declaration from the root node."""
        for child in root_node.children:
            if child.type == 'package_declaration':
                package_identifier = child.child_by_field_name('name')
                if package_identifier:
                    self.package_name = self._get_node_text(package_identifier, source_code)
                break
    
    def _visit_node(self, node: Node, source_code: str):
        """Recursively visit nodes and extract relevant information."""
        if node.type == 'class_declaration':
            self._visit_class(node, source_code)
        elif node.type == 'interface_declaration':
            self._visit_interface(node, source_code)
        elif node.type == 'enum_declaration':
            self._visit_enum(node, source_code)
        elif node.type == 'method_declaration':
            self._visit_method(node, source_code)
        elif node.type == 'constructor_declaration':
            self._visit_constructor(node, source_code)
        
        # Continue visiting children
        for child in node.children:
            self._visit_node(child, source_code)
    
    def _visit_class(self, node: Node, source_code: str):
        """Visit a class declaration node."""
        class_name = self._get_identifier_name(node)
        if not class_name:
            return
        
        full_class_name = self._build_full_name(class_name)
        
        self.nodes.append({
            'name': full_class_name,
            'type': NODE_TYPE_CLASS,
            'code': self._get_node_text(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'modifiers': self._get_modifiers(node),
            'extends': self._get_extends(node, source_code),
            'implements': self._get_implements(node, source_code)
        })
        
        self.node_name_stack.append(class_name)
        self.node_type_stack.append(NODE_TYPE_CLASS)
        
        # Visit class body
        body = node.child_by_field_name('body')
        if body:
            for child in body.children:
                self._visit_node(child, source_code)
        
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _visit_interface(self, node: Node, source_code: str):
        """Visit an interface declaration node."""
        interface_name = self._get_identifier_name(node)
        if not interface_name:
            return
        
        full_interface_name = self._build_full_name(interface_name)
        
        self.nodes.append({
            'name': full_interface_name,
            'type': NODE_TYPE_INTERFACE,
            'code': self._get_node_text(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'modifiers': self._get_modifiers(node),
            'extends': self._get_extends(node, source_code)
        })
        
        self.node_name_stack.append(interface_name)
        self.node_type_stack.append(NODE_TYPE_INTERFACE)
        
        # Visit interface body
        body = node.child_by_field_name('body')
        if body:
            for child in body.children:
                self._visit_node(child, source_code)
        
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _visit_enum(self, node: Node, source_code: str):
        """Visit an enum declaration node."""
        enum_name = self._get_identifier_name(node)
        if not enum_name:
            return
        
        full_enum_name = self._build_full_name(enum_name)
        
        self.nodes.append({
            'name': full_enum_name,
            'type': NODE_TYPE_ENUM,
            'code': self._get_node_text(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'modifiers': self._get_modifiers(node),
            'implements': self._get_implements(node, source_code)
        })
        
        self.node_name_stack.append(enum_name)
        self.node_type_stack.append(NODE_TYPE_ENUM)
        
        # Visit enum body
        body = node.child_by_field_name('body')
        if body:
            for child in body.children:
                self._visit_node(child, source_code)
        
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _visit_method(self, node: Node, source_code: str):
        """Visit a method declaration node."""
        method_name = self._get_identifier_name(node)
        if not method_name:
            return
        
        # Skip constructors (they are handled separately)
        if method_name == self._get_class_name_from_context():
            return
        
        full_method_name = self._build_full_name(method_name)
        
        self.nodes.append({
            'name': full_method_name,
            'parent_type': self.node_type_stack[-1] if self.node_type_stack else None,
            'type': NODE_TYPE_FUNCTION,
            'code': self._get_node_text(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'modifiers': self._get_modifiers(node),
            'return_type': self._get_return_type(node, source_code),
            'parameters': self._get_parameters(node, source_code)
        })
        
        self.node_name_stack.append(method_name)
        self.node_type_stack.append(NODE_TYPE_FUNCTION)
        
        # Visit method body
        body = node.child_by_field_name('body')
        if body:
            for child in body.children:
                self._visit_node(child, source_code)
        
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _visit_constructor(self, node: Node, source_code: str):
        """Visit a constructor declaration node."""
        constructor_name = self._get_identifier_name(node)
        if not constructor_name:
            return
        
        full_constructor_name = self._build_full_name(constructor_name)
        
        self.nodes.append({
            'name': full_constructor_name,
            'parent_type': self.node_type_stack[-1] if self.node_type_stack else None,
            'type': NODE_TYPE_FUNCTION,
            'code': self._get_node_text(node, source_code),
            'start_line': node.start_point[0] + 1,
            'end_line': node.end_point[0] + 1,
            'modifiers': self._get_modifiers(node),
            'parameters': self._get_parameters(node, source_code),
            'is_constructor': True
        })
        
        self.node_name_stack.append(constructor_name)
        self.node_type_stack.append(NODE_TYPE_FUNCTION)
        
        # Visit constructor body
        body = node.child_by_field_name('body')
        if body:
            for child in body.children:
                self._visit_node(child, source_code)
        
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _get_identifier_name(self, node: Node) -> Optional[str]:
        """Get the identifier name from a node."""
        identifier = node.child_by_field_name('name')
        if identifier and identifier.type == 'identifier':
            return identifier.text.decode('utf8')
        return None
    
    def _build_full_name(self, name: str) -> str:
        """Build the full name including package and parent context."""
        name_parts = []
        
        if self.package_name:
            name_parts.append(self.package_name)
        
        name_parts.extend(self.node_name_stack)
        name_parts.append(name)
        
        return '.'.join(name_parts)
    
    def _get_node_text(self, node: Node, source_code: str) -> str:
        """Get the source text for a node."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        return source_code[start_byte:end_byte]
    
    def _get_modifiers(self, node: Node) -> List[str]:
        """Get modifiers from a node."""
        modifiers = []
        for child in node.children:
            if child.type == 'modifiers':
                for modifier_child in child.children:
                    if modifier_child.type in ['public', 'private', 'protected', 'static', 'final', 'abstract']:
                        modifiers.append(modifier_child.type)
        return modifiers
    
    def _get_extends(self, node: Node, source_code: str) -> Optional[str]:
        """Get the extends clause from a node."""
        superclass = node.child_by_field_name('superclass')
        if superclass:
            return self._get_node_text(superclass, source_code).strip()
        return None
    
    def _get_implements(self, node: Node, source_code: str) -> List[str]:
        """Get the implements clause from a node."""
        interfaces = []
        super_interfaces = node.child_by_field_name('super_interfaces')
        if super_interfaces:
            for child in super_interfaces.children:
                if child.type == 'interface_type_list':
                    for interface_child in child.children:
                        if interface_child.type == 'interface_type':
                            interfaces.append(self._get_node_text(interface_child, source_code).strip())
        return interfaces
    
    def _get_return_type(self, node: Node, source_code: str) -> Optional[str]:
        """Get the return type from a method node."""
        return_type = node.child_by_field_name('type')
        if return_type:
            return self._get_node_text(return_type, source_code).strip()
        return None
    
    def _get_parameters(self, node: Node, source_code: str) -> List[Dict[str, str]]:
        """Get parameters from a method/constructor node."""
        parameters = []
        parameters_node = node.child_by_field_name('parameters')
        if parameters_node:
            for child in parameters_node.children:
                if child.type == 'formal_parameter':
                    param_type = child.child_by_field_name('type')
                    param_name = child.child_by_field_name('name')
                    
                    if param_type and param_name:
                        parameters.append({
                            'type': self._get_node_text(param_type, source_code).strip(),
                            'name': param_name.text.decode('utf8')
                        })
        return parameters
    
    def _get_class_name_from_context(self) -> Optional[str]:
        """Get the class name from the current context."""
        for i, node_type in enumerate(reversed(self.node_type_stack)):
            if node_type == NODE_TYPE_CLASS:
                return self.node_name_stack[-(i+1)]
        return None
    
    # Javalang visitor methods
    def _visit_javalang_class(self, node, source_code: str):
        class_name = node.name
        full_class_name = self._build_full_name(class_name)
        start_line = node.position.line if hasattr(node.position, 'line') else 1
        end_line = start_line + 1
        # 处理extends/implements类型安全
        extends_val = None
        if getattr(node, 'extends', None):
            if hasattr(node.extends, 'name'):
                extends_val = node.extends.name
            else:
                extends_val = str(node.extends)
        
        implements_val = []
        if getattr(node, 'implements', None):
            for impl in node.implements:
                if hasattr(impl, 'name'):
                    implements_val.append(impl.name)
                else:
                    implements_val.append(str(impl))
        self.nodes.append({
            'name': full_class_name,
            'type': NODE_TYPE_CLASS,
            'code': str(node),
            'start_line': start_line,
            'end_line': end_line,
            'modifiers': [mod for mod in node.modifiers] if node.modifiers else [],
            'extends': extends_val,
            'implements': implements_val
        })
        self.node_name_stack.append(class_name)
        self.node_type_stack.append(NODE_TYPE_CLASS)
        if node.body:
            for child in node.body:
                if isinstance(child, javalang.tree.MethodDeclaration):
                    self._visit_javalang_method(child, source_code)
                elif isinstance(child, javalang.tree.ConstructorDeclaration):
                    self._visit_javalang_constructor(child, source_code)
                elif isinstance(child, javalang.tree.ClassDeclaration):
                    self._visit_javalang_class(child, source_code)
                elif isinstance(child, javalang.tree.InterfaceDeclaration):
                    self._visit_javalang_interface(child, source_code)
                elif isinstance(child, javalang.tree.EnumDeclaration):
                    self._visit_javalang_enum(child, source_code)
        self.node_name_stack.pop()
        self.node_type_stack.pop()

    def _visit_javalang_interface(self, node, source_code: str):
        interface_name = node.name
        full_interface_name = self._build_full_name(interface_name)
        start_line = node.position.line if hasattr(node.position, 'line') else 1
        end_line = start_line + 1
        self.nodes.append({
            'name': full_interface_name,
            'type': NODE_TYPE_INTERFACE,
            'code': str(node),
            'start_line': start_line,
            'end_line': end_line,
            'modifiers': [mod for mod in node.modifiers] if node.modifiers else [],
            'extends': [ext.name if hasattr(ext, 'name') else str(ext) for ext in node.extends] if node.extends else None
        })
        self.node_name_stack.append(interface_name)
        self.node_type_stack.append(NODE_TYPE_INTERFACE)
        if node.body:
            for child in node.body:
                if isinstance(child, javalang.tree.MethodDeclaration):
                    self._visit_javalang_method(child, source_code)
                elif isinstance(child, javalang.tree.ClassDeclaration):
                    self._visit_javalang_class(child, source_code)
                elif isinstance(child, javalang.tree.InterfaceDeclaration):
                    self._visit_javalang_interface(child, source_code)
                elif isinstance(child, javalang.tree.EnumDeclaration):
                    self._visit_javalang_enum(child, source_code)
        self.node_name_stack.pop()
        self.node_type_stack.pop()

    def _visit_javalang_enum(self, node, source_code: str):
        enum_name = node.name
        full_enum_name = self._build_full_name(enum_name)
        start_line = node.position.line if hasattr(node.position, 'line') else 1
        end_line = start_line + 1
        self.nodes.append({
            'name': full_enum_name,
            'type': NODE_TYPE_ENUM,
            'code': str(node),
            'start_line': start_line,
            'end_line': end_line,
            'modifiers': [mod for mod in node.modifiers] if node.modifiers else [],
            'implements': [impl.name if hasattr(impl, 'name') else str(impl) for impl in node.implements] if node.implements else []
        })
        self.node_name_stack.append(enum_name)
        self.node_type_stack.append(NODE_TYPE_ENUM)
        if node.body:
            for child in node.body:
                if isinstance(child, javalang.tree.MethodDeclaration):
                    self._visit_javalang_method(child, source_code)
                elif isinstance(child, javalang.tree.ClassDeclaration):
                    self._visit_javalang_class(child, source_code)
                elif isinstance(child, javalang.tree.InterfaceDeclaration):
                    self._visit_javalang_interface(child, source_code)
                elif isinstance(child, javalang.tree.EnumDeclaration):
                    self._visit_javalang_enum(child, source_code)
        self.node_name_stack.pop()
        self.node_type_stack.pop()

    def _visit_javalang_method(self, node, source_code: str):
        """Visit a javalang method declaration."""
        method_name = node.name
        full_method_name = self._build_full_name(method_name)
        
        start_line = node.position.line if hasattr(node.position, 'line') else 1
        end_line = start_line + 1  # Approximate
        
        self.nodes.append({
            'name': full_method_name,
            'parent_type': self.node_type_stack[-1] if self.node_type_stack else None,
            'type': NODE_TYPE_FUNCTION,
            'code': str(node),
            'start_line': start_line,
            'end_line': end_line,
            'modifiers': [mod for mod in node.modifiers] if node.modifiers else [],
            'return_type': str(node.return_type) if node.return_type else None,
            'parameters': [str(param) for param in node.parameters] if node.parameters else []
        })
        
        self.node_name_stack.append(method_name)
        self.node_type_stack.append(NODE_TYPE_FUNCTION)
        self.node_name_stack.pop()
        self.node_type_stack.pop()
    
    def _visit_javalang_constructor(self, node, source_code: str):
        """Visit a javalang constructor declaration."""
        constructor_name = node.name
        full_constructor_name = self._build_full_name(constructor_name)
        
        start_line = node.position.line if hasattr(node.position, 'line') else 1
        end_line = start_line + 1  # Approximate
        
        self.nodes.append({
            'name': full_constructor_name,
            'parent_type': self.node_type_stack[-1] if self.node_type_stack else None,
            'type': NODE_TYPE_FUNCTION,
            'code': str(node),
            'start_line': start_line,
            'end_line': end_line,
            'modifiers': [mod for mod in node.modifiers] if node.modifiers else [],
            'parameters': [str(param) for param in node.parameters] if node.parameters else [],
            'is_constructor': True
        })
        
        self.node_name_stack.append(constructor_name)
        self.node_type_stack.append(NODE_TYPE_FUNCTION)
        self.node_name_stack.pop()
        self.node_type_stack.pop()


def analyze_java_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Analyze a Java file and extract classes, interfaces, enums, and methods.
    Returns a list of dicts with keys: name, type, code, start_line, end_line, ...
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
        analyzer = JavaCodeAnalyzer(filepath)
        return analyzer.parse_file()
    except Exception as e:
        print(f"Error analyzing Java file {filepath}: {e}")
        return []


def find_java_imports(filepath: str, repo_path: str) -> List[Dict[str, Any]]:
    """
    Find import statements in a Java file.
    
    Args:
        filepath (str): Path to the Java file
        repo_path (str): Path to the repository root
    
    Returns:
        List[Dict[str, Any]]: List of import statements
    """
    # Try tree-sitter first
    if JAVA_LANGUAGE is not None:
        return _find_java_imports_tree_sitter(filepath, repo_path)
    # Fallback to javalang
    elif JAVALANG_AVAILABLE:
        return _find_java_imports_javalang(filepath, repo_path)
    else:
        return []


def _find_java_imports_tree_sitter(filepath: str, repo_path: str) -> List[Dict[str, Any]]:
    """Find imports using tree-sitter."""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        parser = Parser()
        parser.set_language(JAVA_LANGUAGE)
        tree = parser.parse(bytes(source_code, 'utf8'))
        root_node = tree.root_node
        
        imports = []
        
        for child in root_node.children:
            if child.type == 'import_declaration':
                import_text = child.text.decode('utf8').strip()
                
                # Parse import statement
                if import_text.startswith('import '):
                    import_text = import_text[7:]  # Remove 'import '
                    
                    if import_text.endswith(';'):
                        import_text = import_text[:-1]  # Remove ';'
                    
                    # Handle static imports
                    if import_text.startswith('static '):
                        import_text = import_text[7:]  # Remove 'static '
                        is_static = True
                    else:
                        is_static = False
                    
                    # Handle wildcard imports
                    if import_text.endswith('.*'):
                        module_name = import_text[:-2]
                        imports.append({
                            'type': 'import',
                            'module': module_name,
                            'alias': None,
                            'is_static': is_static,
                            'is_wildcard': True
                        })
                    else:
                        # Regular import
                        parts = import_text.split('.')
                        if len(parts) >= 2:
                            module_name = '.'.join(parts[:-1])
                            entity_name = parts[-1]
                            imports.append({
                                'type': 'from',
                                'module': module_name,
                                'entities': [{'name': entity_name, 'alias': None}],
                                'is_static': is_static,
                                'is_wildcard': False
                            })
        
        return imports
    
    except Exception as e:
        print(f"Error finding imports in Java file {filepath}: {e}")
        return []


def _find_java_imports_javalang(filepath: str, repo_path: str) -> List[Dict[str, Any]]:
    """Find imports using javalang."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            source_code = file.read()
        
        tree = javalang.parse.parse(source_code)
        imports = []
        
        if tree.imports:
            for import_decl in tree.imports:
                import_path = import_decl.path
                
                # Handle wildcard imports
                if import_path.endswith('.*'):
                    module_name = import_path[:-2]
                    imports.append({
                        'type': 'import',
                        'module': module_name,
                        'alias': None,
                        'is_static': False,
                        'is_wildcard': True
                    })
                else:
                    # Regular import
                    parts = import_path.split('.')
                    if len(parts) >= 2:
                        module_name = '.'.join(parts[:-1])
                        entity_name = parts[-1]
                        imports.append({
                            'type': 'from',
                            'module': module_name,
                            'entities': [{'name': entity_name, 'alias': None}],
                            'is_static': False,
                            'is_wildcard': False
                        })
        
        return imports
    
    except Exception as e:
        print(f"Error finding imports with javalang in Java file {filepath}: {e}")
        return []


def resolve_java_module(module_name: str, repo_path: str) -> Optional[str]:
    """
    Resolve a Java module name to a file path in the repo.
    
    Args:
        module_name (str): The module name (e.g., 'com.example.MyClass')
        repo_path (str): Path to the repository root
    
    Returns:
        Optional[str]: The file path if found, or None if not found
    """
    # Convert module name to file path
    parts = module_name.split('.')
    
    # Try to resolve as a .java file
    file_path = os.path.join(repo_path, *parts) + '.java'
    if os.path.isfile(file_path):
        return file_path
    
    # Try to resolve as a class in a package
    if len(parts) >= 2:
        package_path = os.path.join(repo_path, *parts[:-1])
        class_name = parts[-1] + '.java'
        file_path = os.path.join(package_path, class_name)
        if os.path.isfile(file_path):
            return file_path
    
    return None 