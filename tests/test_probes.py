from hypothesis import given, strategies as st

from scorensic import probes

text = st.text(min_size=1, max_size=40)


@given(ref=text, alts=st.lists(text, max_size=3))
def test_negative_probes_never_equal_an_accepted_answer(ref, alts):
    accepted = {probes._norm(x) for x in [ref, *alts]}
    for p in probes.build({"id": "t", "prompt": "q", "reference": ref, "valid_alternatives": alts}):
        assert set(p) >= {"kind", "output", "expect", "confidence"}
        if p["expect"] == "fail":
            assert probes._norm(p["output"]) not in accepted


@given(ref=text)
def test_mutants_change_the_reference(ref):
    for _, m in probes.mutants(ref):
        assert m != ref
