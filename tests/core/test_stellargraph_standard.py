# -*- coding: utf-8 -*-
#
# Copyright 2019 Data61, CSIRO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import pandas as pd
import numpy as np
from stellargraph.core.graph import *


def create_nodes_dict():
    """
    Creates nodes with identifiers and randomised features, in the
    form of a type map:

        { type: data_frame }

    Returns:
        dict: The type -> nodes mapping.
    """
    node_type_specs = [(6, 3, "a"), (4, 5, "b")]
    nodes = {
        node_type: pd.DataFrame(
            {
                **{"id": [f"n_{node_type}_{ii}" for ii in range(num_nodes)]},
                **{f"f{fk}": np.random.randn(num_nodes) for fk in range(num_features)},
            }
        )
        for num_nodes, num_features, node_type in node_type_specs
    }
    return nodes


def create_edges_dict(nodes):
    """
    Creates random edges with identifiers and randomised features, in the
    form of a type map:

        { type: data_frame }

    Args:
        nodes (dict): The type -> nodes mapping.

    Returns:
        dict: The type -> edges mapping.
    """
    edge_type_specs = [(10, 4, "x"), (8, 5, "y")]
    edges = {
        edge_type: pd.DataFrame(
            {
                **{
                    "id": [f"e_{edge_type}_{ii}" for ii in range(num_edges)],
                    "src": [
                        np.random.choice(nodes[k].id)
                        for k in np.random.choice(list(nodes), num_edges)
                    ],
                    "dst": [
                        np.random.choice(nodes[k].id)
                        for k in np.random.choice(list(nodes), num_edges)
                    ],
                },
                **{f"f{fk}": np.random.randn(num_edges) for fk in range(num_features)},
            }
        )
        for num_edges, num_features, edge_type in edge_type_specs
    }
    return edges


def test_typed_standard():
    nodes = create_nodes_dict()
    edges = create_edges_dict(nodes)
    g = StellarGraph(
        edges=edges,
        nodes=nodes,
        source_id="src",
        target_id="dst",
        edge_id="id",
        node_id="id",
    )
    assert not g.is_directed()
    node_ids = {_id for df in nodes.values() for _id in df["id"]}
    counter = 0
    for node_id in g.nodes():
        counter += 1
        assert node_id in node_ids
    assert len(node_ids) == counter
    edge_ids = {_id for df in edges.values() for _id in df["id"]}
    counter = 0
    for edge in g.edges(include_info=True):
        counter += 1
        assert edge[2] in edge_ids
    assert len(edge_ids) == counter


def example_stellar_graph_1(has_features=False, feature_size=10):
    elist = pd.DataFrame([(1, 2), (2, 3), (1, 4), (3, 2)], columns=["src", "dst"])
    if has_features:
        nmat = np.zeros((4, 1 + feature_size))
        for i in range(4):
            nmat[i, 0] = i + 1
            nmat[i, 1:] = (i + 1) * np.ones(feature_size)
        feature_names = ["f{}".format(i) for i in range(feature_size)]
        nlist = pd.DataFrame(nmat, columns=['id'] + feature_names)
        return StellarGraph(
            edges=elist, source_id='src', target_id='dst', default_edge_type='default',
            nodes=nlist, node_id='id', node_features=feature_names, default_node_type='default',
        )
    else:
        return StellarGraph(
            edges=elist, source_id='src', target_id='dst', default_edge_type='default',
        )


def test_null_node_feature():
    sg = example_stellar_graph_1(has_features=True, feature_size=6)
    aa = sg.node_features([1, None, 2, None])
    assert aa.shape == (4, 6)
    assert aa[:, 0] == pytest.approx([1, 0, 2, 0])