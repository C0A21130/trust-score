from tools.engine import Engine

engine = Engine(rpc_url="http://trust-engine:9000")

def test_predict_score():
    contract_address = "0x76B50696B8EFFCA6Ee6Da7F6471110F334536321"
    original, predict = engine.predict_score(contract_address)
    print(original)
    print(predict)
    assert original is not None
    assert predict is not None
