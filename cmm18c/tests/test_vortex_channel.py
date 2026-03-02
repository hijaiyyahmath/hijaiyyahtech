from src.cmm18c.vortex import (
    jim_vector_from_master,
    vortex_mask_from_jim,
    vortex_bit,
    energy_metrics,
)

def test_vc1_mask_is_binary_and_dim(master_fixture):
    # master_fixture: dict letter -> v18
    J = jim_vector_from_master(master_fixture)
    mask = vortex_mask_from_jim(J)
    assert len(mask) == 18
    assert all(x in (0, 1) for x in mask)

def test_vc1_bit_is_0_or_1(master_fixture):
    J = jim_vector_from_master(master_fixture)
    mask = vortex_mask_from_jim(J)
    b = vortex_bit(J, mask)
    assert b in (0, 1)

def test_energy_metrics_rho_is_integer(master_fixture):
    # pick any letter, e.g. Jim itself
    J = jim_vector_from_master(master_fixture)
    e = energy_metrics(J)
    assert isinstance(e.hat_theta, int)
    assert isinstance(e.U, int)
    assert isinstance(e.rho, int)
