from market_analyst.rag.embeddings import HashingEmbedder


def test_embedding_dimension_matches_config():
    emb = HashingEmbedder(dimension=128)
    [vec] = emb.embed(["فولاد مبارکه اصفهان"])
    assert len(vec) == 128


def test_embedding_is_deterministic():
    emb = HashingEmbedder()
    a = emb.embed(["گزارش مالی فولاد"])[0]
    b = emb.embed(["گزارش مالی فولاد"])[0]
    assert a == b


def test_embedding_is_l2_normalized():
    emb = HashingEmbedder()
    [vec] = emb.embed(["رشد سود شرکت در سه ماهه اخیر"])
    norm = sum(v * v for v in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-9


def test_similar_texts_have_higher_similarity_than_unrelated():
    from market_analyst.rag.similarity import cosine_similarity

    emb = HashingEmbedder()
    a, b, c = emb.embed([
        "افزایش سود شرکت فولاد در گزارش سه‌ماهه",
        "رشد سود فولاد در صورت مالی فصلی",
        "هواشناسی امروز بارانی خواهد بود",
    ])
    assert cosine_similarity(a, b) > cosine_similarity(a, c)


def test_empty_text_returns_zero_vector():
    emb = HashingEmbedder(dimension=64)
    [vec] = emb.embed([""])
    assert vec == [0.0] * 64