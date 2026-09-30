import pytest

from market_analyst.rag.similarity import cosine_similarity


def test_identical_vectors_have_similarity_one():
    v = [1.0, 2.0, 3.0]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-9


def test_orthogonal_vectors_have_similarity_zero():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_zero_vector_returns_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_mismatched_dimensions_raise():
    with pytest.raises(ValueError):
        cosine_similarity([1.0], [1.0, 2.0])