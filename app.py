from flask import Flask, request, jsonify
from rdflib import Graph
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 解析 .ttl 并生成 D2 字符串
def ttl_to_d2(graph: Graph) -> str:
    d2_lines = ['// Generated from TTL', 'direction: right']
    nodes = set()
    edges = []

    for s, p, o in graph:
        s_str = s.split('#')[-1] if '#' in s else s.split('/')[-1]
        p_str = p.split('#')[-1] if '#' in p else p.split('/')[-1]
        if isinstance(o, str) or o.startswith("http"):
            o_str = o.split('#')[-1] if '#' in o else o.split('/')[-1]
        else:
            o_str = str(o)

        # 类型处理（加标签）
        if p_str.lower() == 'type':
            nodes.add((s_str, o_str))  # s: 实体, o: 类型
        else:
            edges.append(f'"{s_str}" -> "{o_str}" : {p_str}')
            nodes.add((s_str, None))
            nodes.add((o_str, None))

    # 节点声明
    for node, label in nodes:
        if label:
            d2_lines.append(f'"{node}": "brick:{label}"')
        else:
            d2_lines.append(f'"{node}"')

    # 边连接
    d2_lines.extend(edges)
    return "\n".join(d2_lines)


@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    try:
        g = Graph()
        g.parse(file, format='ttl')
        d2_output = ttl_to_d2(g)
        return jsonify({'d2': d2_output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
