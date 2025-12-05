from app.components.tools.engine import Engine

engine = Engine(
    engine_url="http://trust-engine:9000"
)

def test_predict_score():
    contract_address = "0x32F4866B63CaDeD01058540Cff9Bb1fcC05E1cb7"
    result = engine.predict_score(contract_address)

    # resultに返り値が入ることを確認
    assert result is not None

    # resultが辞書型であることを確認
    assert isinstance(result, dict)

    # resultにキーが存在することを確認
    assert 'original_score' in result
    assert 'predict_score' in result
    assert 'generate_graph' in result

    # 取得したスコアの辞書が0から1の範囲内でありアドレスと紐づけられていることを確認
    for key in ["original_score", "predict_score"]:
        for address, score in result[key].items():
            assert 0 <= score <= 1
            assert address.startswith("0x")

    # generate_graphが要素2つの2次元配列であることを確認
    assert isinstance(result['generate_graph'], list)
    for sublist in result['generate_graph']:
        assert isinstance(sublist, list)
        assert len(sublist) == 2
        assert sublist[0].startswith("0x")
        assert sublist[1].startswith("0x")
    