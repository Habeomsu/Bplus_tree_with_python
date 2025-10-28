class Node:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None ## 리프끼리 연결

class BPlusTree:
    """order는 해당 노드가 가지는 키의 수 -> 자식 수는 order + 1"""
    def __init__(self, order=3):
        self.root = Node(is_leaf=True)  ## 근데 왜 처음 리프 노드로 만드는거지?
        self.order = order

    ## 해당 키값이 비교하는 키보다 작으면 왼쪽으로 간다.
    def _find_leaf(self, node, key):
        """키를 삽입할 리프 노드 탐색"""
        if node.is_leaf:
            return node
        for i, item in enumerate(node.keys):
            if key < item:
                return self._find_leaf(node.children[i], key)
        return self._find_leaf(node.children[-1], key)

    ## b+트리에 새로운 키-쌍을 삽입 -> 만약 order 보다 크면 leaf 분할
    def insert(self, key, value):
        leaf = self._find_leaf(self.root, key)
        self._insert_in_leaf(leaf, key, value)
        ## 리프 분할 (리프 분할을 리프에 삽입후 해준다?)
        if len(leaf.keys) > self.order:
            self._split_leaf(leaf)

    ## 리프 노드에 키-값 삽입 (정렬 유지)
    def _insert_in_leaf(self, leaf, key, value):
        insert_pos = 0
        while insert_pos < len(leaf.keys) and leaf.keys[insert_pos] < key:
            insert_pos += 1
        leaf.keys.insert(insert_pos, key) ## 키 값은 뭐가 다를까??
        leaf.children.insert(insert_pos, value)

    ## 리프 노드 분할
    def _split_leaf(self, leaf):

        ## 새로운 리프를 오른쪽으로 만든다.
        mid = len(leaf.keys) // 2
        new_leaf = Node(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.children = leaf.children[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.children = leaf.children[:mid]
        new_leaf.next = leaf.next
        leaf.next = new_leaf

        ## 루트 노드 변경하기
        if leaf == self.root:
            new_root = Node(is_leaf=False)
            new_root.keys = [new_leaf.keys[0]]
            new_root.children = [leaf, new_leaf]
            self.root = new_root ## 이러면 하나의 노드는 왼쪽 오른쪽만 분해되는거 아닌가?
        else:
            self._insert_in_parent(leaf, new_leaf.keys[0], new_leaf)

    ## 내부 노드 분할 처리
    def _insert_in_parent(self, node, key, new_node):
        parent = self._find_parent(self.root, node)
        if not parent:
            # 부모가 없으면 루트 확장 (부모가 없는게 가능한가?)
            new_root = Node(is_leaf=False)
            new_root.keys = [key]
            new_root.children = [node, new_node]
            self.root = new_root
            return

        insert_pos = 0
        while insert_pos < len(parent.keys) and key > parent.keys[insert_pos]:
            insert_pos += 1
        parent.keys.insert(insert_pos, key)
        parent.children.insert(insert_pos + 1, new_node) ## 왜 여기서는 pos+1 에 삽입할까?

        if len(parent.keys) > self.order:
            self._split_internal(parent)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        new_node = Node(is_leaf=False)
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        promote_key = node.keys[mid]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1] ## 이건 왜 +1 이지

        if node == self.root:
            new_root = Node(is_leaf=False)
            new_root.keys = [promote_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            self._insert_in_parent(node, promote_key, new_node)

    ## DFS로 부모 탐색
    def _find_parent(self, current, child):
        if current.is_leaf or current.children[0].is_leaf: ## 왜 첫번째 자식이 리프노드이면 안될까?
            return None
        for c in current.children:
            if c == child:
                return current
            result = self._find_parent(c, child)
            if result:
                return result
        return None

    ## 탐색
    def search(self, key):
        """단일 키 탐색"""
        node = self._find_leaf(self.root, key)

        for i, k in enumerate(node.keys):
            if k == key:
                print(f"✅ [탐색 성공] Key={key}, Value={node.children[i]}")
                return node.children[i]

        print(f"❌ [탐색 실패] Key={key}는 존재하지 않음")
        return None

    def search_with_trace(self, key):
        """탐색 경로를 출력하면서 키를 찾기"""
        node = self.root
        path = []

        # 리프까지 내려가기
        while not node.is_leaf:
            path.append(node.keys[:])
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        path.append(node.keys[:])

        # 결과 출력
        print("\n🔍 [탐색 경로 추적]")
        for level, keys in enumerate(path):
            print(f"Level {level}: {keys}")

        # 실제 데이터 검색
        for i, k in enumerate(node.keys):
            if k == key:
                print(f"✅ [탐색 성공] Key={key}, Value={node.children[i]}")
                return node.children[i]

        print(f"❌ [탐색 실패] Key={key}는 존재하지 않음")
        return None

    def print_tree(self, node=None, level=0, is_last=True, prefix=""):
        """B+ 트리를 트리 형태로 예쁘게 출력"""
        node = node or self.root
        connector = "└── " if is_last else "├── "
        node_type = "Leaf" if node.is_leaf else "Internal"
        print(prefix + connector + f"[{node_type}] Keys: {node.keys}")

        if not node.is_leaf:
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                self.print_tree(child, level + 1, is_last_child, child_prefix)


if __name__ == '__main__':
    bpt = BPlusTree(order=3)
    bpt.insert(10, "apple")
    bpt.insert(20, "banana")
    bpt.insert(5, "grape")
    bpt.insert(15, "mango")
    bpt.insert(25, "melon")

    print("\n=== B+ 트리 구조 ===")
    bpt.print_tree()

    print("\n=== 단일 탐색 ===")
    bpt.search(15)
    bpt.search(100)

    print("\n=== 경로 추적 탐색 ===")
    bpt.search_with_trace(25)


