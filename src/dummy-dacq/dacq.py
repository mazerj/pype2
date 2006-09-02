# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import time

def dacq_start(dummy1, dummy2, dummy3, dummy4, dummy5):
	return 1

def dacq_stop():
	return 1

def dacq_release():
	return 1

def dacq_dig_in(dummy):
	return 1

def dacq_dig_out(dummy1, dummy2):
	return 1

def dacq_eye_x():
	return 1

def dacq_eye_y():
	return 1

def dacq_eye_params(dummy1, dummy2, dummy3, dummy4):
	return 1

def dacq_eye_read(dummy):
	return 1

def dacq_ad_n(dummy):
	return 1

def dacq_ts():
	return time.time()*1000

def dacq_bar():
	return 1

def dacq_bar_genint(dummy):
	return 1

def dacq_bar_transitions(dummy):
	return 1

def dacq_sw1():
	return 1

def dacq_sw2():
	return 1

def dacq_juice(dummy):
	return 1

def dacq_juice_drip(dummy):
	return 1

def dacq_fixbreak_tau(dummy):
	return 1

def dacq_fixwin(dummy1, dummy2, dummy3, dummy4, dummy5):
	return 1

def dacq_fixwin_genint(dummy1, dummy2):
	return 1

def dacq_fixwin_reset(dummy):
	return 1

def dacq_fixwin_state(dummy):
	return 1

def dacq_fixwin_broke(dummy):
	return 1

def dacq_fixwin_break_time(dummy):
	return 1

def dacq_adbuf_clear():
	pass

def dacq_adbuf_size():
	return 1

def dacq_adbuf_t(dummy):
	return 1

def dacq_adbuf_x(dummy):
	return 1

def dacq_adbuf_y(dummy):
	return 1

def dacq_adbuf_pa(dummy):
	return 1

def dacq_adbuf_c0(dummy):
	return 1

def dacq_adbuf_c1(dummy):
	return 1

def dacq_adbuf_c2(dummy):
	return 1

def dacq_adbuf_c3(dummy):
	return 1

def dacq_adbuf_c4(dummy):
	return 1

def dacq_adbuf_photo(dummy):
	return 1

def dacq_adbuf_spikes(dummy):
	return 1

def dacq_eye_smooth(dummy):
	return 1

def dacq_set_pri(dummy1):
	pass

def dacq_seteuid(dummy):
	return 0

def dacq_set_mypri(dummy):
	return 0

def dacq_set_rt(dummy):
	return 0

def dacq_adbuf_toggle(dummy):
	return 0

def dacq_jsbut(dummy):
	return 0
