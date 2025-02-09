from pymarketng.application.BidsManager import BidsManager
from pymarketng.application.Mechanism import Average_Mechanism_Multi, Leftover_Clear, VCG_Mechanism_Multi


def test_Average_Mechanism_Multi_3():
    bm = BidsManager()
    bm.add(price=1.0, user_id=0, unit=10.0, is_buying=True)
    bm.add(price=1.0, user_id=1, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=2, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=3, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=4, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=5, unit=2.0, is_buying=False)
    bm_new, tm = bm.run((Average_Mechanism_Multi,))

    print(tm.get_df())

    assert bm_new.get_breakeven_single() == 0
    assert tm.get_auctioneer_profit() == 0

    assert tm.get_total_traded_unit_p2p() == 10.0
    assert len(tm.trans) == 5

def test_Average_Mechanism_Multi_1():
    bm = BidsManager()
    bm.add(price=1.0, user_id=0, unit=10.0, is_buying=True)
    bm.add(price=1.0, user_id=1, unit=10.0, is_buying=True)
    bm.add(price=1.0, user_id=2, unit=10.0, is_buying=False)
    bm.add(price=1.0, user_id=3, unit=10.0, is_buying=False)
    bm.add(price=1.0, user_id=4, unit=10.0, is_buying=False)
    bm_new, tm = bm.run((Average_Mechanism_Multi,))

    print(tm.get_total_traded_unit_p2p())
    print(tm.get_players_total_trade_unit())
    
    assert bm_new.get_breakeven_single() == 0
    assert tm.get_auctioneer_profit() == 0

    assert tm.get_total_traded_unit_p2p() == 20.0
    assert len(tm.trans) == 2

def test_LeftOverClear_Mechanism_1():
    bm = BidsManager()
    bm.add(price=1.0, user_id=0, unit=20.0, is_buying=True)
    bm.add(price=1.0, user_id=1, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=2, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=3, unit=2.0, is_buying=False)
    bm.add(price=1.0, user_id=4, unit=2.0, is_buying=False)
    bm_new, tm = bm.run((Average_Mechanism_Multi, Leftover_Clear), 0.5, 2.0)

    assert bm_new.get_breakeven_single() == 0
    assert tm.get_auctioneer_profit() == 0

    assert tm.get_total_traded_unit_p2p() == 8.0
    assert tm.get_players_total_trade_unit() == 20.0
    assert tm.get_players_total_trade_profit() == 32.0
    assert len(tm.trans) == 5

def test_VCG_Mechanism_1():
    bm = BidsManager()
    bm.add(price=2.0, user_id=0, unit=2.0, is_buying=True)
    bm.add(price=1.0, user_id=1, unit=2.0, is_buying=False)
    bm_new, tm = bm.run((VCG_Mechanism_Multi,))

    assert bm_new.get_breakeven_single() == 0
    assert tm.get_auctioneer_profit() == 0


test_VCG_Mechanism_1()

