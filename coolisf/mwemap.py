#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Mapping among MWE, lemma form and sense candidates

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
	Python documentation:
		https://docs.python.org/
	argparse module:
		https://docs.python.org/3/howto/argparse.html
	PEP 257 - Python Docstring Conventions:
		https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

MWE_ERG_PRED_LEMMA = {
'_lift_v_out_rel' : 'lift out'
,'calm_v_down_rel' : 'calm down'
,'fend_v_off_rel' : 'fend off'
,'shake_v_out_rel' : 'shake out'
,'burn_v_down_rel' : 'burn down'
,'tense_v_up_rel' : 'tense up'
,'get_v_back_rel' : 'get back'
,'pipe_v_in_rel' : 'pipe in'
,'tear_v_off_rel' : 'tear off'
,'clam_v_up_rel' : 'clam up'
,'stamp_v_on_rel' : 'stamp on'
,'credit_v_back_rel' : 'credit back'
,'choke_v_off_rel' : 'choke off'
,'bleep_v_out_rel' : 'bleep out'
,'stand_v_up_rel' : 'stand up'
,'crack_v_down_rel' : 'crack down'
,'tip_v_off_rel' : 'tip off'
,'shop_v_around-for_rel' : 'shop around for'
,'take_v_in_rel' : 'take in'
,'spirit_v_away_rel' : 'spirit away'
,'chop_v_up_rel' : 'chop up'
,'notch_v_up_rel' : 'notch up'
,'pump_v_in_rel' : 'pump in'
,'button_v_up_rel' : 'button up'
,'shoo_v_in_rel' : 'shoo in'
,'poke_v_out_rel' : 'poke out'
,'invite_v_in_rel' : 'invite in'
,'lay_v_off_rel' : 'lay off'
,'mess_v_up_rel' : 'mess up'
,'seal_v_off_rel' : 'seal off'
,'scarf_v_down_rel' : 'scarf down'
,'stick_v_up_rel' : 'stick up'
,'trim_v_down_rel' : 'trim down'
,'do_v_in_rel' : 'do in'
,'define_v_away_rel' : 'define away'
,'lift_v_up_rel' : 'lift up'
,'gnaw_v_away_rel' : 'gnaw away'
,'scale_v_up_rel' : 'scale up'
,'back_v_out-of_rel' : 'back out of'
,'burst_v_open_rel' : 'burst open'
,'hold_v_up_rel' : 'hold up on'
,'pay_v_down_rel' : 'pay down'
,'invite_v_out_rel' : 'invite out'
,'towel_v_off_rel' : 'towel off'
,'shove_v_out_rel' : 'shove out'
,'band_v_together_rel' : 'band together'
,'muddle_v_through_rel' : 'muddle through'
,'crack_v_up_rel' : 'crack up'
,'parcel_v_out_rel' : 'parcel out'
,'drive_v_around_rel' : 'drive around'
,'come_v_up_rel' : 'come up'
,'come_v_through_rel' : 'come through'
,'gin_v_up_rel' : 'gin up'
,'carry_v_out_rel' : 'carry out'
,'stand_v_in-for_rel' : 'stand in for'
,'string_v_along_rel' : 'string'
,'cut_v_down_rel' : 'cut down'
,'strike_v_off_rel' : 'strike off'
,'pull_v_away_rel' : 'pull away'
,'filter_v_out_rel' : 'filter out'
,'puff_v_up_rel' : 'puff up'
,'follow_v_around_rel' : 'follow around'
,'break_v_off_rel' : 'break off'
,'wipe_v_off_rel' : 'wipe off'
,'come_v_out_rel' : 'come out'
,'whip_v_off_rel' : 'whip off'
,'warm_v_over_rel' : 'warm over'
,'mark_v_out_rel' : 'mark out'
,'load_v_up_rel' : 'load up'
,'fuck_v_off_rel' : 'fuck off'
,'look_v_out_rel' : 'look out'
,'stay_v_over_rel' : 'stay over'
,'bus_v_in_rel' : 'bus in'
,'hole_v_up_rel' : 'hole up'
,'flare_v_up_rel' : 'flare up'
,'start_v_off_rel' : 'start off'
,'cover_v_up_rel' : 'cover up'
,'space_v_out_rel' : 'space out'
,'scrape_v_away_rel' : 'scrape away'
,'bulk_v_up_rel' : 'bulk up'
,'fumble_v_around_rel' : 'fumble around'
,'have_v_back_rel' : 'have back'
,'mop_v_up_rel' : 'mop up'
,'put_v_off_rel' : 'put off'
,'face_v_up_rel' : 'face up'
,'haul_v_away_rel' : 'haul away'
,'freak_v_out_rel' : 'freak out'
,'put_v_down_rel' : 'put down'
,'work_v_up_rel' : 'work up'
,'copy_v_down_rel' : 'copy down'
,'dig_v_out_rel' : 'dig out'
,'spin_v_out_rel' : 'spin out'
,'bottle_v_up_rel' : 'bottle up'
,'log_v_out_rel' : 'log out'
,'listen_v_in_rel' : 'listen in'
,'mess_v_around_rel' : 'mess around'
,'shoo_v_away_rel' : 'shoo away'
,'smash_v_in_rel' : 'smash in'
,'whistle_v_up_rel' : 'whistle up'
,'let_v_down_rel' : 'let down'
,'clear_v_off_rel' : 'clear off'
,'phase_v_in_rel' : 'phase in'
,'bubble_v_over_rel' : 'bubble over'
,'pull_v_apart_rel' : 'pull apart'
,'mull_v_over_rel' : 'mull over'
,'charge_v_off_rel' : 'charge off'
,'schedule_v_in_rel' : 'schedule in'
,'let_v_on_rel' : 'let on'
,'hand_v_in_rel' : 'hand in'
,'slacken_v_off_rel' : 'slacken off'
,'curtain_v_off_rel' : 'curtain off'
,'blast_v_out_rel' : 'blast out'
,'use_v_up_rel' : 'use up'
,'add_v_up_rel' : 'add up'
,'drop_v_out_rel' : 'drop out'
,'draft_v_in_rel' : 'draft in'
,'pop_v_out_rel' : 'pop out'
,'bring_v_together_rel' : 'bring together'
,'shove_v_in_rel' : 'shove in'
,'ship_v_back_rel' : 'ship back'
,'wear_v_out_rel' : 'wear out'
,'bail_v_out_rel' : 'bail out'
,'yield_v_up_rel' : 'yield up'
,'chime_v_in_rel' : 'chime in'
,'give_v_in_rel' : 'give in'
,'bang_v_up_rel' : 'bang up'
,'rough_v_in_rel' : 'rough in'
,'sack_v_out_rel' : 'sack out'
,'bog_v_down_rel' : 'bog down'
,'tease_v_open_rel' : 'tease open'
,'screw_v_up_rel' : 'screw up'
,'hang_v_about_rel' : 'hang about'
,'scrape_v_together_rel' : 'scrape together'
,'laugh_v_off_rel' : 'laugh off'
,'run_v_up_rel' : 'run up'
,'level_v_out_rel' : 'level out'
,'muscle_v_out_rel' : 'muscle out'
,'fling_v_off_rel' : 'fling off'
,'fork_v_over_rel' : 'fork over'
,'search_v_out_rel' : 'search out'
,'lay_v_down_rel' : 'lay down'
,'haul_v_out_rel' : 'haul out'
,'button_v_down_rel' : 'button down'
,'freeze_v_up_rel' : 'freeze up'
,'hot_v_up_rel' : 'hot up'
,'go_v_out_rel' : 'go out'
,'pull_v_off_rel' : 'pull off'
,'finish_v_up_rel' : 'finish'
,'stave_v_off_rel' : 'stave off'
,'have_v_yet_rel' : 'have yet'
,'grow_v_up_rel' : 'grow up'
,'sop_v_up_rel' : 'sop up'
,'jot_v_down_rel' : 'jot down'
,'ground_v_out_rel' : 'ground out'
,'copy_v_out_rel' : 'copy out'
,'cash_v_in_rel' : 'cash in'
,'hand_v_over_rel' : 'hand over'
,'blast_v_away_rel' : 'blast away'
,'write_v_out_rel' : 'write out'
,'trim_v_off_rel' : 'trim off'
,'hand_v_down_rel' : 'hand down'
,'doll_v_up_rel' : 'doll up'
,'catch_v_on_rel' : 'catch on'
,'smooth_v_over_rel' : 'smooth over'
,'talk_v_up_rel' : 'talk up'
,'crank_v_out_rel' : 'crank out'
,'divide_v_up_rel' : 'divide up'
,'ride_v_in_rel' : 'ride in'
,'call_v_up_rel' : 'call up'
,'parachute_v_in_rel' : 'parachute in'
,'opt_v_out_rel' : 'opt out'
,'lop_v_off_rel' : 'lop off'
,'dash_v_out_rel' : 'dash out'
,'pick_v_up_rel' : 'pick up'
,'act_v_up_rel' : 'act up'
,'cheer_v_up_rel' : 'cheer up'
,'die_v_away_rel' : 'die away'
,'build_v_up_rel' : 'build up'
,'tie_v_on_rel' : 'tie on'
,'die_v_off_rel' : 'die off'
,'divide_v_off_rel' : 'divide off'
,'break_v_out_rel' : 'break out'
,'cram_v_in_rel' : 'cram in'
,'frighten_v_off_rel' : 'frighten off'
,'tote_v_up_rel' : 'tote up'
,'weigh_v_up_rel' : 'weigh up'
,'rust_v_in_rel' : 'rust in'
,'coop_v_up_rel' : 'coop up'
,'pull_v_up_rel' : 'pull up'
,'draw_v_aside_rel' : 'draw aside'
,'let_v_off_rel' : 'let off'
,'tease_v_apart_rel' : 'tease apart'
,'look_v_up-to_rel' : 'look up to'
,'cough_v_up_rel' : 'cough up'
,'pop_v_down_rel' : 'pop down'
,'seal_v_out_rel' : 'seal out'
,'fling_v_open_rel' : 'fling open'
,'scrape_v_up_rel' : 'scrape up'
,'sleep_v_off_rel' : 'sleep off'
,'stretch_v_out_rel' : 'stretch out'
,'pop_v_off_rel' : 'pop off'
,'move_v_up_rel' : 'move up'
,'brick_v_up_rel' : 'brick up'
,'start_v_up_rel' : 'start up'
,'settle_v_down_rel' : 'settle down'
,'drive_v_down_rel' : 'drive down'
,'call_v_off_rel' : 'call off'
,'siphon_v_off_rel' : 'siphon off'
,'want_v_back_rel' : 'want back'
,'swell_v_up_rel' : 'swell up'
,'keep_v_up_rel' : 'keep up'
,'make_v_out_rel' : 'make out'
,'go_v_away_rel' : 'go away'
,'roll_v_over_rel' : 'roll over'
,'take_v_along_rel' : 'take along'
,'hunt_v_up_rel' : 'hunt up'
,'speak_v_out_rel' : 'speak out'
,'work_v_in_rel' : 'work in'
,'give_v_out_rel' : 'give out'
,'draw_v_back_rel' : 'draw back'
,'bring_v_back_rel' : 'bring back'
,'stir_v_in_rel' : 'stir in'
,'pull_v_in_rel' : 'pull in'
,'let_v_go-of_rel' : 'let go of'
,'boil_v_up_rel' : 'boil up'
,'crisp_v_up_rel' : 'crisp up'
,'phase_v_out_rel' : 'phase out'
,'clamp_v_down_rel' : 'clamp down on'
,'scare_v_off_rel' : 'scare off'
,'back_v_out_rel' : 'back out'
,'edge_v_out_rel' : 'edge out'
,'drive_v_home_rel' : 'drive home'
,'wheel_v_out_rel' : 'wheel out'
,'bust_v_open_rel' : 'bust open'
,'back_v_off_rel' : 'back off'
,'lock_v_up_rel' : 'lock up'
,'wake_v_up_rel' : 'wake x up'
,'dry_v_up_rel' : 'dry up'
,'shine_v_out_rel' : 'shine out'
,'eat_v_in_rel' : 'eat in'
,'leave_v_open_rel' : 'leave open'
,'slack_v_off_rel' : 'slack off'
,'pull_v_back_rel' : 'pull back'
,'sponge_v_off-of_rel' : 'sponge off of'
,'crack_v_open_rel' : 'crack open'
,'write_v_in_rel' : 'write in'
,'tangle_v_up_rel' : 'tangle up'
,'strip_v_down_rel' : 'strip down'
,'ward_v_off_rel' : 'ward off'
,'strip_v_off_rel' : 'strip off'
,'hack_v_up_rel' : 'hack up'
,'jack_v_up_rel' : 'jack up'
,'plug_v_in_rel' : 'plug in'
,'pluck_v_out_rel' : 'pluck out'
,'lock_v_out_rel' : 'lock out'
,'lead_v_on_rel' : 'lead on'
,'weed_v_out_rel' : 'weed out'
,'free_v_up_rel' : 'free'
,'mount_v_up_rel' : 'mount up'
,'serve_v_up_rel' : 'serve up'
,'raise_v_up_rel' : 'raise up'
,'stick_v_out_rel' : 'stick out'
,'take_v_x-off_rel' : 'take off'
,'clear_v_up_rel' : 'clear up'
,'bring_v_about_rel' : 'bring about'
,'pare_v_off_rel' : 'pare off'
,'play_v_up_rel' : 'play up'
,'fire_v_up_rel' : 'fire'
,'add_v_on_rel' : 'add on'
,'clock_v_in_rel' : 'clock in'
,'shake_v_off_rel' : 'shake off'
,'cut_v_in_rel' : 'cut in'
,'beg_v_off_rel' : 'beg off'
,'snuggle_v_up_rel' : 'snuggle up'
,'get_v_off_rel' : 'get off'
,'turn_v_off_rel' : 'turn off'
,'screen_v_out_rel' : 'screen out'
,'pack_v_in_rel' : 'pack in'
,'smooth_v_out_rel' : 'smooth out'
,'square_v_up_rel' : 'square up'
,'make_v_up-of_rel' : 'make up'
,'come_v_in_rel' : 'come in'
,'code_v_up_rel' : 'code up'
,'damp_v_down_rel' : 'damp down'
,'pipe_v_up_rel' : 'pipe up'
,'bow_v_out_rel' : 'bow out'
,'slip_v_in_rel' : 'slip in'
,'hold_v_still_rel' : 'hold still'
,'separate_v_out_rel' : 'separate out'
,'send_v_back_rel' : 'send back'
,'tell_v_off_rel' : 'tell off'
,'warm_v_up_rel' : 'warm up'
,'run_v_over_rel' : 'run over'
,'shout_v_out_rel' : 'shout out'
,'reel_v_off_rel' : 'reel off'
,'track_v_down_rel' : 'track down'
,'boot_v_out_rel' : 'boot out'
,'fill_v_in_rel' : 'fill in'
,'talk_v_over_rel' : 'talk over'
,'clog_v_up_rel' : 'clog up'
,'sink_v_in_rel' : 'sink in'
,'cross_v_out_rel' : 'cross out'
,'type_v_out_rel' : 'type out'
,'abstract_v_away_rel' : 'abstract away'
,'look_v_over_rel' : 'look over'
,'dig_v_up_rel' : 'dig up'
,'set_v_forth_rel' : 'set forth'
,'move_v_about_rel' : 'move about'
,'put_v_forth_rel' : 'put forth'
,'burn_v_off_rel' : 'burn off'
,'smuggle_v_in_rel' : 'smuggle in'
,'tap_v_off_rel' : 'tap off'
,'let_v_in_rel' : 'let in'
,'look_v_around_rel' : 'look around'
,'line_v_up_rel' : 'line up'
,'gut_v_out_rel' : 'gut out'
,'scrape_v_off_rel' : 'scrape off'
,'drive_v_off_rel' : 'drive off'
,'render_v_up_rel' : 'render up'
,'tease_v_out_rel' : 'tease out'
,'bomb_v_out_rel' : 'bomb out'
,'set_v_in_rel' : 'set in'
,'lock_v_away_rel' : 'lock away'
,'mix_v_up_rel' : 'mix up'
,'shut_v_off_rel' : 'shut off'
,'rest_v_up_rel' : 'rest up'
,'leave_v_out_rel' : 'leave out'
,'go_v_on_rel' : 'go on'
,'chat_v_up_rel' : 'chat up'
,'beam_v_out_rel' : 'beam out'
,'beat_v_up_rel' : 'beat up'
,'pop_v_up_rel' : 'pop up'
,'squirrel_v_away_rel' : 'squirrel away'
,'tear_v_open_rel' : 'tear open'
,'press_v_in_rel' : 'press in'
,'push_v_back_rel' : 'push back'
,'fog_v_up_rel' : 'fog up'
,'firm_v_up_rel' : 'firm up'
,'speak_v_up_rel' : 'speak up'
,'point_v_up_rel' : 'point up'
,'hold_v_on_rel' : 'hold on'
,'fit_v_in_rel' : 'fit in with'
,'turn_v_back_rel' : 'turn back'
,'leave_v_off_rel' : 'leave off'
,'think_v_through_rel' : 'think through'
,'drop_v_in_rel' : 'drop in'
,'simmer_v_down_rel' : 'simmer down'
,'want_v_out-of_rel' : 'want out of'
,'head_v_on_rel' : 'head on'
,'polish_v_up_rel' : 'polish up'
,'hurry_v_up_rel' : 'hurry up'
,'cool_v_down_rel' : 'cool down'
,'stiffen_v_up_rel' : 'stiffen up'
,'weigh_v_in_rel' : 'weigh in'
,'cotton_v_on_rel' : 'cotton on'
,'winch_v_in_rel' : 'winch in'
,'harness_v_up_rel' : 'harness up'
,'wear_v_on_rel' : 'wear on'
,'stink_v_up_rel' : 'stink up'
,'wear_v_away_rel' : 'wear away'
,'buff_v_up_rel' : 'buff up'
,'run_v_around_rel' : 'run around'
,'cut_v_apart_rel' : 'cut apart'
,'sleep_v_in_rel' : 'sleep in'
,'hunker_v_down_rel' : 'hunker down'
,'water_v_down_rel' : 'water down'
,'fly_v_in_rel' : 'fly in'
,'glaze_v_over_rel' : 'glaze over'
,'work_v_out_rel' : 'work out'
,'tear_v_up_rel' : 'tear up'
,'eat_v_out_rel' : 'eat out'
,'seek_v_out_rel' : 'seek out'
,'fork_v_off_rel' : 'fork off'
,'pair_v_up_rel' : 'pair up'
,'inch_v_up_rel' : 'inch up'
,'haul_v_up_rel' : 'haul up'
,'rust_v_away_rel' : 'rust away'
,'lay_v_out_rel' : 'lay out'
,'board_v_up_rel' : 'board up'
,'air_v_out_rel' : 'air out'
,'hash_v_out_rel' : 'hash out'
,'bump_v_off_rel' : 'bump off'
,'go_v_ahead_rel' : 'go ahead'
,'log_v_off_rel' : 'log off'
,'plunk_v_down_rel' : 'plunk down'
,'switch_v_off_rel' : 'switch off'
,'chase_v_away_rel' : 'chase away'
,'branch_v_off_rel' : 'branch off'
,'summon_v_up_rel' : 'summon up'
,'box_v_up_rel' : 'box up'
,'pull_v_out_rel' : 'pull out'
,'sound_v_out_rel' : 'sound out'
,'move_v_in_rel' : 'move in'
,'drown_v_out_rel' : 'drown out'
,'mush_v_together_rel' : 'mush together'
,'shop_v_around_rel' : 'shop around'
,'total_v_up_rel' : 'total up'
,'type_v_up_rel' : 'type up'
,'stop_v_by_rel' : 'stop by'
,'back_v_up_rel' : 'back up'
,'heat_v_up-cause_rel' : 'heat up'
,'scoop_v_out_rel' : 'scoop out'
,'set_v_about_rel' : 'set about'
,'beef_v_up_rel' : 'beef up'
,'wind_v_up_rel' : 'wind up'
,'live_v_out_rel' : 'live out'
,'bed_v_down_rel' : 'bed down'
,'factor_v_in_rel' : 'factor in'
,'ease_v_out_rel' : 'ease out'
,'pin_v_on_rel' : 'pin on'
,'throttle_v_back_rel' : 'throttle back'
,'cut_v_up_rel' : 'cut up'
,'split_v_off_rel' : 'split off'
,'shoot_v_up_rel' : 'shoot up'
,'want_v_out_rel' : 'want out'
,'ease_v_up_rel' : 'ease up'
,'look_v_up_rel' : 'look up'
,'carve_v_out_rel' : 'carve out'
,'drive_v_in_rel' : 'drive in'
,'cling_v_on_rel' : 'cling on'
,'break_v_in_rel' : 'break in'
,'save_v_up_rel' : 'save up'
,'cross_v_off_rel' : 'cross off'
,'put_v_in_rel' : 'put in'
,'polish_v_off_rel' : 'polish off'
,'average_v_out_rel' : 'average out'
,'gasp_v_out_rel' : 'gasp out'
,'clean_v_out_rel' : 'clean out'
,'wipe_v_out_rel' : 'wipe out'
,'spark_v_off_rel' : 'spark off'
,'fight_v_off_rel' : 'fight off'
,'snuff_v_out_rel' : 'snuff out'
,'drink_v_up_rel' : 'drink up'
,'narrow_v_down_rel' : 'narrow down'
,'add_v_up-to_rel' : 'add up to'
,'ferret_v_out_rel' : 'ferret out'
,'round_v_down_rel' : 'round down'
,'block_v_off_rel' : 'block off'
,'hunt_v_down_rel' : 'hunt down'
,'draw_v_forth_rel' : 'draw forth'
,'lag_v_behind_rel' : 'lag behind'
,'close_v_off_rel' : 'close off'
,'round_v_out_rel' : 'round out'
,'thin_v_out_rel' : 'thin out'
,'root_v_around_rel' : 'root around'
,'wedge_v_in_rel' : 'wedge in'
,'gouge_v_away_rel' : 'gouge away'
,'point_v_out-to_rel' : 'point out'
,'pick_v_off_rel' : 'pick off'
,'hold_v_out_rel' : 'hold out'
,'put_v_by_rel' : 'put by'
,'push_v_aside_rel' : 'push aside'
,'sign_v_up_rel' : 'sign up'
,'move_v_on_rel' : 'move on'
,'hand_v_off_rel' : 'hand off'
,'slug_v_down_rel' : 'slug down'
,'etch_v_away_rel' : 'etch away'
,'max_v_out_rel' : 'max out'
,'stamp_v_out_rel' : 'stamp out'
,'scout_v_out_rel' : 'scout out'
,'carry_v_in_rel' : 'carry in'
,'try_v_out_rel' : 'try out'
,'push_v_away_rel' : 'push away'
,'fly_v_on_rel' : 'fly on'
,'fight_v_back_rel' : 'fight back'
,'last_v_out_rel' : 'last out'
,'peel_v_off_rel' : 'peel off'
,'close_v_up_rel' : 'close up'
,'fork_v_out_rel' : 'fork out'
,'string_v_on_rel' : 'string'
,'push_v_in_rel' : 'push in'
,'soak_v_up_rel' : 'soak up'
,'carve_v_up_rel' : 'carve up'
,'lay_v_up_rel' : 'lay up'
,'squeeze_v_out_rel' : 'squeeze out'
,'open_v_up_rel' : 'open up'
,'go_v_through_rel' : 'go through'
,'set_v_up_rel' : 'set up'
,'boil_v_down-to_rel' : 'boil down'
,'drag_v_out_rel' : 'drag out'
,'come_v_along_rel' : 'come along'
,'sign_v_off_rel' : 'sign off'
,'find_v_out_rel' : 'find out'
,'throw_v_up_rel' : 'throw up'
,'hunt_v_out_rel' : 'hunt out'
,'pull_v_down_rel' : 'pull down'
,'dress_v_down_rel' : 'dress down'
,'pal_v_around_rel' : 'pal around'
,'pass_v_out_rel' : 'pass out'
,'grease_v_up_rel' : 'grease up'
,'rocket_v_up_rel' : 'rocket up'
,'pitch_v_in_rel' : 'pitch in'
,'bite_v_out_rel' : 'bite out'
,'spill_v_over_rel' : 'spill over'
,'knuckle_v_down_rel' : 'knuckle down'
,'iron_v_out_rel' : 'iron out'
,'draw_v_up_rel' : 'draw up'
,'burn_v_out_rel' : 'burn out'
,'turn_v_down_rel' : 'turn down'
,'nod_v_off_rel' : 'nod off'
,'suck_v_up_rel' : 'suck up to'
,'shape_v_up_rel' : 'shape up'
,'put_v_up_rel' : 'put up'
,'fall_v_in_rel' : 'fall in'
,'build_v_in_rel' : 'build in'
,'prop_v_open_rel' : 'prop open'
,'stroll_v_along_rel' : 'stroll along'
,'take_v_down_rel' : 'take down'
,'head_v_out_rel' : 'head out'
,'smooth_v_away_rel' : 'smooth away'
,'belt_v_out_rel' : 'belt out'
,'contract_v_out_rel' : 'contract out'
,'send_v_out_rel' : 'send out'
,'mete_v_out_rel' : 'mete out'
,'write_v_back_rel' : 'write back'
,'bend_v_over_rel' : 'bend over'
,'call_v_out_rel' : 'call out'
,'trim_v_away_rel' : 'trim away'
,'trail_v_off_rel' : 'trail off'
,'hoist_v_up_rel' : 'hoist up'
,'bandage_v_up_rel' : 'bandage up'
,'pull_v_open_rel' : 'pull open'
,'reel_v_out_rel' : 'reel out'
,'march_v_off_rel' : 'march off'
,'head_v_up_rel' : 'head up'
,'buoy_v_up_rel' : 'buoy up'
,'dry_v_out_rel' : 'dry out'
,'schlep_v_around_rel' : 'schlep around'
,'break_v_away_rel' : 'break away'
,'run_v_out_rel' : 'run out'
,'blur_v_out_rel' : 'blur out'
,'follow_v_up_rel' : 'follow up'
,'strike_v_down_rel' : 'strike down'
,'scare_v_away_rel' : 'scare away'
,'spin_v_around_rel' : 'spin around'
,'chase_v_down_rel' : 'chase down'
,'tune_v_out_rel' : 'tune out'
,'brush_v_away_rel' : 'brush away'
,'pass_v_off_rel' : 'pass off'
,'draw_v_away_rel' : 'draw away'
,'slip_v_on_rel' : 'slip on'
,'set_v_off_rel' : 'set off'
,'come_v_about_rel' : 'come about'
,'line_v_out_rel' : 'line out'
,'nail_v_down_rel' : 'nail down'
,'luck_v_out_rel' : 'luck out'
,'steal_v_away_rel' : 'steal away'
,'wake_v_up_rel' : 'wake up'
,'chase_v_up_rel' : 'chase up'
,'make_v_up_rel' : 'make up'
,'perk_v_up_rel' : 'perk up'
,'fuck_v_around_rel' : 'fuck around'
,'roll_v_up_rel' : 'roll up'
,'wash_v_up_rel' : 'wash up'
,'slap_v_down_rel' : 'slap down'
,'muddle_v_along_rel' : 'muddle along'
,'chip_v_away_rel' : 'chip away'
,'pump_v_out_rel' : 'pump out'
,'take_v_apart_rel' : 'take apart'
,'sock_v_in_rel' : 'sock in'
,'shy_v_away_rel' : 'shy away'
,'ship_v_out_rel' : 'ship out'
,'pay_v_up_rel' : 'pay up'
,'pump_v_up_rel' : 'pump up'
,'flip_v_out_rel' : 'flip out'
,'winnow_v_out_rel' : 'winnow out'
,'stash_v_away_rel' : 'stash away'
,'scrub_v_off_rel' : 'scrub off'
,'squeeze_v_in_rel' : 'squeeze in'
,'blast_v_open_rel' : 'blast open'
,'build_v_on_rel' : 'build on'
,'flunk_v_out_rel' : 'flunk out'
,'drop_v_by_rel' : 'drop by'
,'frame_v_in_rel' : 'frame in'
,'mail_v_in_rel' : 'mail in'
,'slice_v_out_rel' : 'slice out'
,'grow_v_over_rel' : 'grow over'
,'sand_v_down_rel' : 'sand down'
,'meet_v_up_rel' : 'meet up'
,'gouge_v_out_rel' : 'gouge out'
,'home_v_in_rel' : 'home in'
,'suck_v_up_rel' : 'suck up'
,'want_v_in_rel' : 'want in'
,'break_v_through_rel' : 'break through'
,'play_v_down_rel' : 'play down'
,'read_v_off_rel' : 'read off'
,'fix_v_up_rel' : 'fix up'
,'scar_v_up_rel' : 'scar up'
,'hold_v_in_rel' : 'hold in'
,'snatch_v_up_rel' : 'snatch up'
,'cry_v_out_rel' : 'cry out'
,'sweat_v_off_rel' : 'sweat off'
,'hang_v_on_rel' : 'hang on'
,'flatten_v_out_rel' : 'flatten out'
,'quiet_v_down_rel' : 'quiet down'
,'look_v_in_rel' : 'look in on'
,'gas_v_up_rel' : 'gas up'
,'pay_v_out_rel' : 'pay out'
,'pass_v_up_rel' : 'pass up'
,'slip_v_off_rel' : 'slip off'
,'gather_v_up_rel' : 'gather up'
,'put_v_out_rel' : 'put out'
,'let_v_up_rel' : 'let up'
,'hem_v_out_rel' : 'hem out'
,'haul_v_off_rel' : 'haul off'
,'wrap_v_up_rel' : 'wrap up'
,'palm_v_off_rel' : 'palm off'
,'freshen_v_up_rel' : 'freshen up'
,'get_v_through_rel' : 'get through'
,'drift_v_off_rel' : 'drift off'
,'auction_v_off_rel' : 'auction off'
,'winch_v_up_rel' : 'winch up'
,'rush_v_out_rel' : 'rush out'
,'read_v_in_rel' : 'read in'
,'spin_v_off_rel' : 'spin off'
,'bust_v_up_rel' : 'bust up'
,'knock_v_out_rel' : 'knock out'
,'do_v_up_rel' : 'do up'
,'live_v_down_rel' : 'live down'
,'watch_v_out_rel' : 'watch out'
,'heave_v_out_rel' : 'heave out'
,'wash_v_out_rel' : 'wash out'
,'bring_v_out_rel' : 'bring out'
,'branch_v_out_rel' : 'branch out'
,'team_v_up_rel' : 'team up'
,'square_v_away_rel' : 'square away'
,'write_v_down_rel' : 'write down'
,'win_v_over_rel' : 'win over'
,'stand_v_out_rel' : 'stand out'
,'flush_v_out_rel' : 'flush out'
,'grey_v_out_rel' : 'grey out'
,'call_v_in_rel' : 'call in'
,'fling_v_back_rel' : 'fling back'
,'bring_v_off_rel' : 'bring off'
,'blot_v_out_rel' : 'blot out'
,'stop_v_in_rel' : 'stop in'
,'pass_v_along_rel' : 'pass along'
,'walk_v_over_rel' : 'walk over'
,'crop_v_up_rel' : 'crop up'
,'roll_v_down_rel' : 'roll down'
,'tone_v_down_rel' : 'tone down'
,'check_v_out-of_rel' : 'check out of'
,'give_v_off_rel' : 'give off'
,'pig_v_out_rel' : 'pig out'
,'whip_v_out_rel' : 'whip out'
,'grind_v_out_rel' : 'grind out'
,'bring_v_forth_rel' : 'bring forth'
,'print_v_out_rel' : 'print out'
,'kick_v_out_rel' : 'kick out'
,'lump_v_in_rel' : 'lump in'
,'sound_v_off_rel' : 'sound off'
,'throw_v_in_rel' : 'throw in'
,'pass_v_on_rel' : 'pass on'
,'blank_v_out_rel' : 'blank out'
,'rinse_v_out_rel' : 'rinse out'
,'chalk_v_up_rel' : 'chalk up'
,'sit_v_down_rel' : 'sit down'
,'bowl_v_over_rel' : 'bowl over'
,'wheel_v_in_rel' : 'wheel in'
,'bat_v_away_rel' : 'bat away'
,'back_v_down_rel' : 'back down'
,'set_v_out_rel' : 'set out'
,'pick_v_out_rel' : 'pick out'
,'carry_v_away_rel' : 'carry away'
,'boot_v_up_rel' : 'boot up'
,'stick_v_in_rel' : 'stick in'
,'keep_v_on_rel' : 'keep'
,'pack_v_up_rel' : 'pack up'
,'eke_v_out_rel' : 'eke out'
,'snap_v_in_rel' : 'snap in'
,'comb_v_out_rel' : 'comb out'
,'gun_v_down_rel' : 'gun down'
,'juggle_v_around_rel' : 'juggle around'
,'straighten_v_out_rel' : 'straighten out'
,'touch_v_off_rel' : 'touch off'
,'bawl_v_out_rel' : 'bawl out'
,'lift_v_off_rel' : 'lift off'
,'louse_v_up_rel' : 'louse up'
,'cut_v_out_rel' : 'cut out'
,'hold_v_onto_rel' : 'hold on to'
,'scratch_v_up_rel' : 'scratch'
,'bubble_v_up_rel' : 'bubble up'
,'bum_v_around_rel' : 'bum around'
,'turn_v_out_rel' : 'turn out expl'
,'peter_v_out_rel' : 'peter out'
,'get_v_down-to_rel' : 'get down to'
,'like_v_back_rel' : 'like back'
,'scale_v_back_rel' : 'scale back'
,'settle_v_in_rel' : 'settle in'
,'snap_v_off_rel' : 'snap off'
,'scrub_v_out_rel' : 'scrub out'
,'chop_v_off_rel' : 'chop off'
,'back_v_away_rel' : 'back away'
,'send_v_in_rel' : 'send in'
,'sum_v_up_rel' : 'sum up'
,'let_v_out_rel' : 'let out'
,'pour_v_in_rel' : 'pour in'
,'trace_v_down_rel' : 'trace down'
,'usher_v_in_rel' : 'usher in'
,'crowd_v_out_rel' : 'crowd out'
,'get_v_on_rel' : 'get on with'
,'spill_v_out_rel' : 'spill out'
,'tack_v_down_rel' : 'tack down'
,'find_v_out-about_rel' : 'find out'
,'log_v_in_rel' : 'log in'
,'drag_v_in_rel' : 'drag in'
,'pony_v_up_rel' : 'pony up'
,'kit_v_out_rel' : 'kit out'
,'put_v_together_rel' : 'put together'
,'take_v_back_rel' : 'take back'
,'shell_v_out_rel' : 'shell out'
,'roll_v_out_rel' : 'roll out'
,'smuggle_v_out_rel' : 'smuggle out'
,'buy_v_back_rel' : 'buy back'
,'cut_v_off_rel' : 'cut off'
,'show_v_up_rel' : 'show up'
,'drag_v_down_rel' : 'drag down'
,'haul_v_in_rel' : 'haul in'
,'rig_v_up_rel' : 'rig up'
,'heat_v_up_rel' : 'heat up'
,'quieten_v_down_rel' : 'quieten down'
,'turn_v_in_rel' : 'turn in'
,'clamp_v_down_rel' : 'clamp down'
,'tuck_v_in_rel' : 'tuck in'
,'close_v_down_rel' : 'close down'
,'root_v_out_rel' : 'root out'
,'leave_v_behind_rel' : 'leave behind'
,'tee_v_off_rel' : 'tee off'
,'measure_v_up_rel' : 'measure up'
,'rub_v_off_rel' : 'rub off'
,'knock_v_over_rel' : 'knock over'
,'rack_v_up_rel' : 'rack up'
,'saddle_v_up_rel' : 'saddle up'
,'come_v_across_rel' : 'come across'
,'strip_v_away_rel' : 'strip away'
,'plant_v_out_rel' : 'plant out'
,'jump_v_up_rel' : 'jump up'
,'get_v_along_rel' : 'get along'
,'rip_v_off_rel' : 'rip off'
,'send_v_around_rel' : 'send around'
,'hitch_v_up_rel' : 'hitch up'
,'stop_v_off_rel' : 'stop off'
,'live_v_up_rel' : 'live up'
,'break_v_open_rel' : 'break open'
,'rust_v_out_rel' : 'rust out'
,'turn_v_up_rel' : 'turn up'
,'bite_v_off_rel' : 'bite off'
,'rip_v_up_rel' : 'rip up'
,'slough_v_off_rel' : 'slough off'
,'blow_v_away_rel' : 'blow away'
,'come_v_back_rel' : 'come back'
,'tank_v_up_rel' : 'tank up'
,'paste_v_in_rel' : 'paste in'
,'bring_v_down_rel' : 'bring down'
,'puff_v_out_rel' : 'puff out'
,'win_v_back_rel' : 'win back'
,'start_v_over_rel' : 'start over'
,'hook_v_up_rel' : 'hook up'
,'tip_v_over_rel' : 'tip over'
,'lace_v_up_rel' : 'lace up'
,'ring_v_up_rel' : 'ring'
,'ration_v_out_rel' : 'ration out'
,'come_v_around_rel' : 'come around'
,'throw_v_out_rel' : 'throw out'
,'shore_v_up_rel' : 'shore up'
,'rein_v_in_rel' : 'rein in'
,'wall_v_off_rel' : 'wall off'
,'straighten_v_up_rel' : 'straighten up'
,'stress_v_out_rel' : 'stress out'
,'isolate_v_out_rel' : 'isolate out'
,'store_v_up_rel' : 'store up'
,'link_v_up_rel' : 'link up'
,'bottom_v_out_rel' : 'bottom out'
,'brush_v_off_rel' : 'brush off'
,'shovel_v_out_rel' : 'shovel out'
,'take_v_off_rel' : 'take off'
,'bounce_v_back_rel' : 'bounce back'
,'horn_v_in_rel' : 'horn in on'
,'fool_v_around_rel' : 'fool around'
,'wrest_v_away_rel' : 'wrest away'
,'take_v_aback_rel' : 'take aback'
,'wash_v_away_rel' : 'wash away'
,'push_v_down_rel' : 'push down'
,'shrug_v_off_rel' : 'shrug off'
,'power_v_down_rel' : 'power down'
,'dredge_v_up_rel' : 'dredge up'
,'bundle_v_up_rel' : 'bundle up'
,'thrash_v_out_rel' : 'thrash out'
,'buy_v_up_rel' : 'buy up'
,'throw_v_over_rel' : 'throw over'
,'even_v_out_rel' : 'even out'
,'clear_v_away_rel' : 'clear away'
,'cancel_v_out_rel' : 'cancel out'
,'scribble_v_down_rel' : 'scribble down'
,'walk_v_off_rel' : 'walk off'
,'strike_v_up_rel' : 'strike up'
,'conjure_v_up_rel' : 'conjure up'
,'stand_v_up-for_rel' : 'stand up for'
,'lash_v_out_rel' : 'lash out'
,'deck_v_out_rel' : 'deck out'
,'dish_v_out_rel' : 'dish out'
,'whisk_v_away_rel' : 'whisk away'
,'soap_v_up_rel' : 'soap up'
,'pile_v_on_rel' : 'pile on'
,'slam_v_down_rel' : 'slam down'
,'give_v_back_rel' : 'give back'
,'bring_v_forward_rel' : 'bring forward'
,'string_v_together_rel' : 'string'
,'bring_v_in_rel' : 'bring in'
,'spit_v_out_rel' : 'spit out'
,'count_v_out_rel' : 'count out'
,'jet_v_off_rel' : 'jet off'
,'break_v_up_rel' : 'break up'
,'do_v_away-with_rel' : 'do away'
,'lock_v_down_rel' : 'lock down'
,'carry_v_on_rel' : 'carry on'
,'move_v_out_rel' : 'move out'
,'fly_v_off_rel' : 'fly off'
,'tire_v_out_rel' : 'tire out'
,'bring_v_up_rel' : 'bring up'
,'tack_v_up_rel' : 'tack up'
,'loan_v_out_rel' : 'loan out'
,'sprawl_v_out_rel' : 'sprawl out'
,'buy_v_out_rel' : 'buy out'
,'pile_v_up_rel' : 'pile up'
,'screw_v_in_rel' : 'screw in'
,'round_v_up_rel' : 'round up'
,'sort_v_out_rel' : 'sort out'
,'snap_v_up_rel' : 'snap up'
,'push_v_open_rel' : 'push open'
,'split_v_up_rel' : 'split up'
,'close_v_in_rel' : 'close in'
,'shack_v_up-with_rel' : 'shack up'
,'boil_v_down_rel' : 'boil down'
,'leave_v_in_rel' : 'leave in'
,'die_v_out_rel' : 'die out'
,'match_v_up_rel' : 'match up'
,'spring_v_up_rel' : 'spring up'
,'clean_v_up_rel' : 'clean up'
,'map_v_out_rel' : 'map out'
,'seal_v_up_rel' : 'seal up'
,'put_v_aside_rel' : 'put aside'
,'seize_v_up_rel' : 'seize up'
,'ramp_v_up_rel' : 'ramp up'
,'fake_v_out_rel' : 'fake out'
,'look_v_back-at_rel' : 'look back at'
,'black_v_out_rel' : 'black out'
,'stall_v_off_rel' : 'stall off'
,'ramp_v_down_rel' : 'ramp down'
,'cook_v_up_rel' : 'cook up'
,'marry_v_off_rel' : 'marry off'
,'throw_v_open_rel' : 'throw open'
,'melt_v_down_rel' : 'melt down'
,'put_v_on_rel' : 'put on'
,'wander_v_up_rel' : 'wander up'
,'break_v_even_rel' : 'break even'
,'take_v_up_rel' : 'take up'
,'dial_v_in_rel' : 'dial in'
,'shoot_v_down_rel' : 'shoot down'
,'come_v_across_rel' : 'come across as'
,'touch_v_down_rel' : 'touch down'
,'rabbit_v_on_rel' : 'rabbit on'
,'crank_v_up_rel' : 'crank up'
,'get_v_out_rel' : 'get out'
,'scoop_v_up_rel' : 'scoop up'
,'dress_v_up_rel' : 'dress up'
,'go_v_off_rel' : 'go off'
,'sober_v_up_rel' : 'sober up'
,'kill_v_off_rel' : 'kill off'
,'fritter_v_away_rel' : 'fritter away'
,'come_v_over_rel' : 'come over'
,'cast_v_off_rel' : 'cast off'
,'play_v_out_rel' : 'play out'
,'chew_v_out_rel' : 'chew out'
,'bear_v_out_rel' : 'bear out'
,'roar_v_out_rel' : 'roar out'
,'drink_v_down_rel' : 'drink down'
,'single_v_out_rel' : 'single out'
,'pour_v_out_rel' : 'pour out'
,'get_v_up_rel' : 'get up'
,'taper_v_off_rel' : 'taper off'
,'yank_v_out_rel' : 'yank out'
,'pencil_v_in_rel' : 'pencil in'
,'kick_v_off_rel' : 'kick off'
,'blurt_v_out_rel' : 'blurt out'
,'patch_v_in_rel' : 'patch in'
,'piss_v_off_rel' : 'piss off'
,'slurp_v_up_rel' : 'slurp up'
,'snuggle_v_down_rel' : 'snuggle down'
,'hold_v_back_rel' : 'hold back'
,'put_v_back_rel' : 'put back'
,'cut_v_back_rel' : 'cut back'
,'buy_v_off_rel' : 'buy off'
,'trade_v_in_rel' : 'trade in'
,'weigh_v_down_rel' : 'weigh down'
,'butt_v_in_rel' : 'butt in'
,'take_v_out_rel' : 'take out'
,'amp_v_up_rel' : 'amp up'
,'hear_v_back-from_rel' : 'hear back from'
,'rub_v_out_rel' : 'rub out'
,'cut_v_short_rel' : 'cut short'
,'read_v_out_rel' : 'read out'
,'do_v_so_rel' : 'do so'
,'blow_v_down_rel' : 'blow down'
,'close_v_out_rel' : 'close out'
,'wind_v_down_rel' : 'wind down'
,'chill_v_out_rel' : 'chill out'
,'lose_v_out_rel' : 'lose out'
,'sniff_v_out_rel' : 'sniff out'
,'ice_v_over_rel' : 'ice over'
,'box_v_in_rel' : 'box in'
,'switch_v_on_rel' : 'switch on'
,'tune_v_up_rel' : 'tune up'
,'psyche_v_out_rel' : 'psyche out'
,'cheer_v_on_rel' : 'cheer on'
,'steam_v_open_rel' : 'steam open'
,'sharpen_v_up_rel' : 'sharpen up'
,'finish_v_off_rel' : 'finish off'
,'head_v_off_rel' : 'head off'
,'stop_v_over_rel' : 'stop over'
,'get_v_around_rel' : 'get around'
,'whack_v_off_rel' : 'whack off'
,'let_v_go-of_rel' : 'let go'
,'factor_v_out_rel' : 'factor out'
,'wear_v_thin_rel' : 'wear thin'
,'pin_v_down_rel' : 'pin down to'
,'enter_v_in_rel' : 'enter in'
,'match_v_up_rel' : 'match up to'
,'buck_v_up_rel' : 'buck up'
,'mark_v_off_rel' : 'mark off'
,'slow_v_down_rel' : 'slow down'
,'bring_v_home_rel' : 'bring home'
,'dream_v_up_rel' : 'dream up'
,'look_v_on_rel' : 'look on'
,'pass_v_over_rel' : 'pass over'
,'mask_v_out_rel' : 'mask out'
,'get_v_in_rel' : 'get in'
,'sweep_v_away_rel' : 'sweep away'
,'clown_v_around_rel' : 'clown around'
,'top_v_off_rel' : 'top off'
,'hollow_v_out_rel' : 'hollow out'
,'drive_v_up_rel' : 'drive up'
,'chatter_v_on_rel' : 'chatter on'
,'spread_v_out_rel' : 'spread out'
,'gear_v_up_rel' : 'gear up'
,'shut_v_up_rel' : 'shut up'
,'soup_v_up_rel' : 'soup up'
,'suck_v_out_rel' : 'suck out'
,'shove_v_through_rel' : 'shove through'
,'blast_v_off_rel' : 'blast off'
,'cast_v_down_rel' : 'cast down'
,'look_v_out_rel' : 'look out for'
,'check_v_in_rel' : 'check in'
,'whip_v_in_rel' : 'whip in'
,'spell_v_out_rel' : 'spell out'
,'dump_v_out_rel' : 'dump out'
,'well_v_up_rel' : 'well up'
,'hook_v_up_rel' : 'hook up with'
,'drive_v_out_rel' : 'drive out'
,'wander_v_off_rel' : 'wander off'
,'catch_v_up_rel' : 'catch up'
,'strap_v_up_rel' : 'strap up'
,'fill_v_out_rel' : 'fill out'
,'lose_v_out_rel' : 'lose out on'
,'bottle_v_in_rel' : 'bottle in'
,'finish_v_up_rel' : 'finish up'
,'show_v_off_rel' : 'show off'
,'hose_v_down_rel' : 'hose down'
,'turn_v_out_rel' : 'turn out'
,'knuckle_v_under_rel' : 'knuckle under'
,'scale_v_down_rel' : 'scale down'
,'boil_v_over_rel' : 'boil over'
,'die_v_down_rel' : 'die down'
,'flick_v_off_rel' : 'flick off'
,'blow_v_out_rel' : 'blow out'
,'knock_v_off_rel' : 'knock off'
,'strike_v_out_rel' : 'strike out'
,'sell_v_out_rel' : 'sell out'
,'keep_v_up_rel' : 'keep up with'
,'wolf_v_down_rel' : 'wolf down'
,'end_v_up_rel' : 'end up'
,'step_v_up_rel' : 'step up'
,'lift_v_away_rel' : 'lift away'
,'pour_v_off_rel' : 'pour off'
,'fly_v_over_rel' : 'fly over'
,'pull_v_on_rel' : 'pull on'
,'stretch_v_over_rel' : 'stretch over'
,'fuck_v_up_rel' : 'fuck up'
,'flick_v_on_rel' : 'flick on'
,'spruce_v_up_rel' : 'spruce up'
,'whip_v_up_rel' : 'whip up'
,'date_v_back_rel' : 'date back'
,'churn_v_out_rel' : 'churn out'
,'hang_v_up_rel' : 'hang up'
,'ferry_v_in_rel' : 'ferry in'
,'damp_v_out_rel' : 'damp out'
,'swallow_v_up_rel' : 'swallow up'
,'blow_v_up_rel' : 'blow up'
,'trace_v_back_rel' : 'trace back'
,'pour_v_down_rel' : 'pour down'
,'shout_v_back_rel' : 'shout back'
,'nudge_v_up_rel' : 'nudge up'
,'hand_v_out_rel' : 'hand out'
,'gum_v_up_rel' : 'gum up'
,'pull_v_through_rel' : 'pull through'
,'listen_v_up_rel' : 'listen up'
,'seal_v_in_rel' : 'seal in'
,'put_v_through_rel' : 'put through'
,'push_v_off_rel' : 'push off'
,'hang_v_out_rel' : 'hang out'
,'set_v_aside_rel' : 'set aside'
,'soften_v_up_rel' : 'soften up'
,'jam_v_up_rel' : 'jam up'
,'skip_v_out_rel' : 'skip out'
,'pull_v_over_rel' : 'pull over'
,'come_v_up_rel' : 'come up with'
,'scarf_v_up_rel' : 'scarf up'
,'bring_v_along_rel' : 'bring along'
,'slice_v_off_rel' : 'slice off'
,'hew_v_out_rel' : 'hew out'
,'rent_v_out_rel' : 'rent out'
,'flake_v_off_rel' : 'flake off'
,'hold_v_off_rel' : 'hold off'
,'sand_v_off_rel' : 'sand off'
,'ride_v_out_rel' : 'ride out'
,'summon_v_forth_rel' : 'summon forth'
,'pluck_v_up_rel' : 'pluck up'
,'lay_v_on_rel' : 'lay on'
,'knot_v_up_rel' : 'knot up'
,'drag_v_on_rel' : 'drag on'
,'put_v_forward_rel' : 'put forward'
,'camp_v_out_rel' : 'camp out'
,'chew_v_off_rel' : 'chew off'
,'double_v_up_rel' : 'double up'
,'narrow_v_down-to_rel' : 'narrow down'
,'tie_v_up_rel' : 'tie up'
,'gang_v_up_rel' : 'gang up'
,'drum_v_up_rel' : 'drum up'
,'make_v_up-for_rel' : 'make up for'
,'stub_v_out_rel' : 'stub out'
,'toss_v_away_rel' : 'toss away'
,'light_v_up_rel' : 'light up'
,'clutter_v_up_rel' : 'clutter up'
,'cart_v_away_rel' : 'cart away'
,'babble_v_on_rel' : 'babble on'
,'grandfather_v_in_rel' : 'grandfather in'
,'pucker_v_up_rel' : 'pucker up'
,'trot_v_out_rel' : 'trot out'
,'send_v_off_rel' : 'send off'
,'fit_v_in_rel' : 'fit in'
,'rough_v_out_rel' : 'rough out'
,'ask_v_off_rel' : 'ask off'
,'wipe_v_up_rel' : 'wipe up'
,'scrape_v_out_rel' : 'scrape out'
,'call_v_forth_rel' : 'call forth'
,'drop_v_off_rel' : 'drop off'
,'flesh_v_out_rel' : 'flesh out'
,'knock_v_up_rel' : 'knock up'
,'get_v_around-to_rel' : 'get around'
,'break_v_down_rel' : 'break down'
,'vote_v_down_rel' : 'vote down'
,'shut_v_out_rel' : 'shut out'
,'pull_v_across_rel' : 'pull across'
,'check_v_up-on_rel' : 'check up on'
,'block_v_out_rel' : 'block out'
,'size_v_up_rel' : 'size up'
,'slim_v_down_rel' : 'slim down'
,'leave_v_home_rel' : 'leave home'
,'hide_v_away_rel' : 'hide away'
,'put_v_away_rel' : 'put away'
,'reach_v_out_rel' : 'reach out'
,'keep_v_out_rel' : 'keep out'
,'level_v_off_rel' : 'level off'
,'choke_v_up_rel' : 'choke up'
,'figure_v_out_rel' : 'figure out'
,'go_v_along_rel' : 'go along with'
,'puzzle_v_out_rel' : 'puzzle out'
,'cave_v_in_rel' : 'cave in'
,'press_v_on_rel' : 'press on'
,'swoop_v_up_rel' : 'swoop up'
,'start_v_out_rel' : 'start out'
,'hunch_v_up_rel' : 'hunch up'
,'wash_v_down_rel' : 'wash down'
,'hang_v_around_rel' : 'hang around'
,'dam_v_up_rel' : 'dam up'
,'zone_v_out_rel' : 'zone out'
,'crash_v_out_rel' : 'crash out'
,'rule_v_out_rel' : 'rule out'
,'kick_v_around_rel' : 'kick around'
,'pin_v_down_rel' : 'pin down'
,'bow_v_down_rel' : 'bow down'
,'muddle_v_up_rel' : 'muddle up'
,'flag_v_down_rel' : 'flag down'
,'step_v_out_rel' : 'step out'
,'coil_v_up_rel' : 'coil up'
,'rub_v_in_rel' : 'rub in'
,'nose_v_around_rel' : 'nose around'
,'shave_v_off_rel' : 'shave off'
,'thrust_v_out_rel' : 'thrust out'
,'wear_v_off_rel' : 'wear off'
,'give_v_away_rel' : 'give away'
,'tidy_v_up_rel' : 'tidy up'
,'give_v_up_rel' : 'give up'
,'silt_v_up_rel' : 'silt up'
,'clear_v_out_rel' : 'clear out'
,'brush_v_aside_rel' : 'brush aside'
,'pay_v_off_rel' : 'pay off'
,'tune_v_in_rel' : 'tune in'
,'mail_v_back_rel' : 'mail back'
,'drive_v_away_rel' : 'drive away'
,'gamble_v_away_rel' : 'gamble away'
,'speed_v_up_rel' : 'speed up'
,'shut_v_down_rel' : 'shut down'
,'limit_v_down_rel' : 'limit down'
,'kick_v_up_rel' : 'kick up'
,'fish_v_out_rel' : 'fish out'
,'soak_v_in_rel' : 'soak in'
,'keel_v_over_rel' : 'keel over'
,'poke_v_up_rel' : 'poke up'
,'ride_v_up_rel' : 'ride up'
,'book_v_up_rel' : 'book up'
,'act_v_out_rel' : 'act out'
,'write_v_off_rel' : 'write off'
,'fess_v_up_rel' : 'fess up'
,'slap_v_on_rel' : 'slap on'
,'spurt_v_out_rel' : 'spurt out'
,'pare_v_down_rel' : 'pare down'
,'push_v_through_rel' : 'push through'
,'run_v_back_rel' : 'run back'
,'take_v_on_rel' : 'take on'
,'kick_v_in_rel' : 'kick in'
,'slam_v_on_rel' : 'slam on'
,'fall_v_back_rel' : 'fall back'
,'sweat_v_out_rel' : 'sweat out'
,'hold_v_up_rel' : 'hold up'
,'mark_v_down_rel' : 'mark down'
,'push_v_up_rel' : 'push up'
,'scrunch_v_up_rel' : 'scrunch up'
,'patch_v_up_rel' : 'patch up'
,'wall_v_in_rel' : 'wall in'
,'stack_v_up_rel' : 'stack up'
,'dig_v_in_rel' : 'dig in'
,'read_v_over_rel' : 'read over'
,'type_v_in_rel' : 'type in'
,'ball_v_up_rel' : 'ball up'
,'truss_v_up_rel' : 'truss up'
,'eat_v_up_rel' : 'eat up'
,'rave_v_on_rel' : 'rave on'
,'have_v_off_rel' : 'have off'
,'piece_v_together_rel' : 'piece together'
,'prop_v_up_rel' : 'prop up'
,'look_v_up-dir_rel' : 'look up'
,'draw_v_down_rel' : 'draw down'
,'set_v_out-aim_rel' : 'set out'
,'figure_v_in_rel' : 'figure in'
,'turn_v_over_rel' : 'turn over'
,'push_v_forward_rel' : 'push forward'
,'miss_v_out_rel' : 'miss out'
,'wring_v_out_rel' : 'wring out'
,'leave_v_over_rel' : 'leave over'
,'queue_v_up_rel' : 'queue up'
,'charge_v_up_rel' : 'charge up'
,'dry_v_off_rel' : 'dry off'
,'bone_v_up_rel' : 'bone up'
,'laugh_v_away_rel' : 'laugh away'
,'match_v_up_rel' : 'match up with'
,'note_v_down_rel' : 'note down'
,'tie_v_in_rel' : 'tie in'
,'join_v_in_rel' : 'join in'
,'stir_v_up_rel' : 'stir up'
,'round_v_off_rel' : 'round off'
,'soak_v_off_rel' : 'soak off'
,'check_v_out_rel' : 'check out'
,'spur_v_on_rel' : 'spur on'
,'stick_v_around_rel' : 'stick around'
,'nail_v_up_rel' : 'nail up'
,'burn_v_up_rel' : 'burn up'
,'run_v_out-of_rel' : 'run out'
,'tack_v_on_rel' : 'tack on'
,'reel_v_in_rel' : 'reel in'
,'shake_v_up_rel' : 'shake up'
,'throw_v_away_rel' : 'throw away'
,'log_v_on_rel' : 'log on'
,'key_v_in_rel' : 'key in'
,'tick_v_off_rel' : 'tick off'
,'sit_v_out_rel' : 'sit out'
,'hold_v_down_rel' : 'hold down'
,'turn_v_around_rel' : 'turn around'
,'tighten_v_up_rel' : 'tighten up'
,'chip_v_in_rel' : 'chip in'
,'ham_v_up_rel' : 'ham up'
,'hammer_v_out_rel' : 'hammer out'
,'come_v_out_rel' : 'come out with'
,'duck_v_out_rel' : 'duck out'
,'fry_v_up_rel' : 'fry up'
,'lock_v_on_rel' : 'lock on'
,'bring_v_over_rel' : 'bring over'
,'come_v_together_rel' : 'come together'
,'stock_v_up_rel' : 'stock up'
,'snow_v_in_rel' : 'snow in'
,'lock_v_in_rel' : 'lock in'
,'suck_v_in_rel' : 'suck in'
,'cool_v_off_rel' : 'cool off'
,'chop_v_down_rel' : 'chop down'
,'sign_v_on_rel' : 'sign on'
,'sweep_v_up_rel' : 'sweep up'
,'vomit_v_up_rel' : 'vomit up'
,'swear_v_in_rel' : 'swear in'
,'snow_v_under_rel' : 'snow under'
,'dole_v_out_rel' : 'dole out'
,'gobble_v_up_rel' : 'gobble up'
,'send_v_around_rel' : 'send round'
,'take_v_away_rel' : 'take away'
,'knock_v_down_rel' : 'knock down'
,'help_v_out_rel' : 'help out'
,'smash_v_up_rel' : 'smash up'
,'tear_v_apart_rel' : 'tear apart'
,'pin_v_up_rel' : 'pin up'
,'tail_v_off_rel' : 'tail off'
,'shoo_v_out_rel' : 'shoo out'
,'get_v_down_rel' : 'get down'
,'sell_v_off_rel' : 'sell off'
,'feed_v_in_rel' : 'feed in'
,'slow_v_up_rel' : 'slow up'
,'fence_v_in_rel' : 'fence in'
,'stand_v_in_rel' : 'stand in'
,'mail_v_out_rel' : 'mail out'
,'call_v_back_rel' : 'call back'
,'gray_v_out_rel' : 'gray out'
,'add_v_in_rel' : 'add in'
,'take_v_over_rel' : 'take over'
,'take_v_home_rel' : 'take home'
,'gulp_v_down_rel' : 'gulp down'
,'write_v_up_rel' : 'write up'
,'look_v_forward-to_rel' : 'look forward'
,'run_v_off_rel' : 'run off'
,'turn_v_on_rel' : 'turn on'
,'balance_v_out_rel' : 'balance out'
,'short_v_out_rel' : 'short out'
,'shoot_v_off_rel' : 'shoot off'
,'rope_v_together_rel' : 'rope together'
,'think_v_up_rel' : 'think up'
,'cast_v_out_rel' : 'cast out'
,'hike_v_up_rel' : 'hike up'
,'swallow_v_down_rel' : 'swallow down'
,'slice_v_up_rel' : 'slice up'
,'hide_v_out_rel' : 'hide out'
,'set_v_apart_rel' : 'set apart'
,'come_v_on_rel' : 'come on'
,'hem_v_in_rel' : 'hem in'
,'power_v_up_rel' : 'power up'
,'blow_v_off_rel' : 'blow off'
,'pipe_v_down_rel' : 'pipe down'
}

MWE_ERG_WN_MAPPING = {
	"_level_v_off_rel": ["00356649-v"] # level off
	,"hike_v_up_rel": ["01593134-v", "01975912-v"] # hike up
	,"soak_v_up_rel": ["01539063-v", "00601043-v"] # soak up
	,"bow_v_down_rel": ["02063610-v", "00898691-v"] # bow down
	,"come_v_about_rel": ["00339934-v"] # come about
	,"ramp_v_up_rel": ["00253277-v"] # ramp up
	,"break_v_even_rel": ["02280018-v", "02007237-v"] # break even
	,"drive_v_off_rel": ["02002720-v"] # drive off
	,"come_v_together_rel": ["02054541-v"] # come together
	,"bite_v_out_rel": ["00985706-v"] # bite out
	,"knuckle_v_down_rel": ["02421199-v"] # knuckle down
	,"single_v_out_rel": ["00679239-v", "02512305-v"] # single out
	,"reel_v_off_rel": ["01523520-v", "00945648-v"] # reel off
	,"lead_v_on_rel": ["00783956-v", "02575082-v"] # lead on
	,"take_v_off_rel": ["02014165-v", "00179060-v", "02014553-v", "02411950-v", "01743313-v", "00050454-v", "01864438-v", "01326323-v", "00641252-v"] # take off
	,"bomb_v_out_rel": ["01132541-v"] # bomb out
	,"bring_v_back_rel": ["02078294-v", "00022099-v"] # bring back
	,"dig_v_out_rel": ["02143756-v", "01312261-v", "01311103-v"] # dig out
	,"close_v_down_rel": ["02426395-v"] # close down
	,"put_v_in_rel": ["00187526-v", "02281093-v", "00780191-v", "01569566-v", "01072641-v", "00914769-v"] # put in
	,"fire_v_up_rel": ["07302836-n", "00986938-n", "13480848-n", "03343560-n", "14842847-n", "07481375-n", "14686186-n", "07420435-n", "06711159-n", "01135783-v", "01133825-v", "00320536-v", "02402825-v", "01134238-v", "02002410-v", "01759326-v", "00378664-v", "02356420-v"] # fire
	,"cast_v_off_rel": ["01513430-v", "01671609-v"] # cast off
	,"turn_v_in_rel": ["02017775-v", "02293321-v", "01649809-v", "00017865-v"] # turn in
	,"ride_v_out_rel": ["02619122-v"] # ride out
	,"board_v_up_rel": ["01235224-v"] # board up
	,"get_v_through_rel": ["00484892-v", "02709277-v", "02021921-v", "00743344-v", "00591755-v"] # get through
	,"fool_v_around_rel": ["00854150-v", "02598642-v"] # fool around
	,"win_v_back_rel": ["01111570-v"] # win back
	,"carve_v_out_rel": ["01758526-v", "00587675-v"] # carve out
	,"break_v_up_rel": ["02030424-v", "02431320-v", "02029663-v", "01562061-v", "00778275-v", "00447309-v", "01785579-v", "01657977-v", "01610463-v", "01560984-v", "01442578-v", "01215017-v", "00364297-v", "00355955-v", "00355803-v", "00338071-v", "00330565-v", "00209174-v", "00030366-v"] # break up
	,"vote_v_down_rel": ["02473688-v", "02462030-v"] # vote down
	,"pass_v_over_rel": ["00616498-v", "01915365-v", "01912159-v", "01840092-v", "01392237-v"] # pass over
	,"try_v_out_rel": ["02531625-v", "02532886-v", "01718535-v", "01195299-v"] # try out
	,"drown_v_out_rel": ["02172534-v"] # drown out
	,"log_v_off_rel": ["02249293-v"] # log off
	,"come_v_over_rel": ["01063529-v"] # come over
	,"pay_v_out_rel": ["02301502-v"] # pay out
	,"dry_v_up_rel": ["00211108-v", "00242205-v"] # dry up
	,"take_v_over_rel": ["02274482-v", "02381726-v", "02412175-v", "02301825-v", "02274299-v", "02595662-v", "02346724-v", "02216560-v"] # take over
	,"play_v_out_rel": ["02280869-v", "01715185-v", "01081652-v", "00572788-v"] # play out
	,"get_v_back_rel": ["01111570-v", "01153762-v", "01092128-v"] # get back
	,"use_v_up_rel": ["01157517-v", "02267989-v"] # use up
	,"give_v_back_rel": ["02284951-v"] # give back
	,"burn_v_up_rel": ["02762806-v", "01205000-v", "00377351-v"] # burn up
	,"chip_v_away_rel": ["00180315-v"] # chip away
	,"hold_v_off_rel": ["01117325-v", "02641463-v"] # hold off
	,"put_v_together_rel": ["01656788-v"] # put together
	,"cut_v_out_rel": ["00472671-v", "01554799-v", "01440646-v", "01549719-v", "01104509-v", "00352310-v", "00663468-s"] # cut out
	,"back_v_off_rel": ["01997680-v", "02380980-v"] # back off
	,"cough_v_up_rel": ["02200341-v", "00006238-v"] # cough up
	,"lock_v_away_rel": ["01347678-v"] # lock away
	,"kit_v_out_rel": ["02341200-v"] # kit out
	,"bawl_v_out_rel": ["00824767-v"] # bawl out
	,"sound_v_off_rel": ["01027668-v", "01651110-v", "00907147-v"] # sound off
	,"walk_v_off_rel": ["02322433-v", "02010082-v"] # walk off
	,"set_v_off_rel": ["01643657-v", "02014165-v", "00514463-v", "00306723-v", "02717831-v", "00349785-v", "00851239-v"] # set off
	,"rent_v_out_rel": ["02209499-v"] # rent out
	,"team_v_up_rel": ["01089285-v"] # team up
	,"look_v_on_rel": ["02128653-v", "00689950-v"] # look on
	,"break_v_through_rel": ["00539770-v", "00426749-v", "00548266-v"] # break through
	,"frame_v_in_rel": ["01586850-v"] # frame in
	,"take_v_up_rel": ["00348422-v", "00602112-v", "02591171-v", "02649493-v", "02379528-v", "02346724-v", "01982395-v", "01540449-v", "01312371-v", "01540844-v", "01539063-v", "01197980-v", "00350283-v"] # take up
	,"sell_v_off_rel": ["02244248-v"] # sell off
	,"tune_v_up_rel": ["00295966-v", "00295346-v"] # tune up
	,"whisk_v_away_rel": ["01435128-v"] # whisk away
	,"gather_v_up_rel": ["01976089-v", "02305586-v"] # gather up
	,"squeeze_v_out_rel": ["02404076-v", "02239997-v", "01349318-v", "02239846-v", "01675780-v", "01375637-v"] # squeeze out
	,"wind_v_up_rel": ["00352558-v", "02087979-v", "01762283-v", "01522052-v"] # wind up
	,"act_v_up_rel": ["02517655-v", "02122522-v"] # act up
	,"quiet_v_down_rel": ["02190188-v"] # quiet down
	,"tee_v_off_rel": ["01084170-v"] # tee off
	,"perk_v_up_rel": ["00023473-v", "00022686-v"] # perk up
	,"walk_v_over_rel": ["01102667-v"] # walk over
	,"break_v_off_rel": ["00362805-v", "00362348-v", "01259691-v", "01298931-v", "01259458-v"] # break off
	,"thin_v_out_rel": ["00430370-v", "00430494-v", "00226071-v"] # thin out
	,"sell_v_out_rel": ["02247584-v", "00936763-v"] # sell out
	,"box_v_in_rel": ["02711721-v"] # box in
	,"wring_v_out_rel": ["01349318-v"] # wring out
	,"go_v_on_rel": ["02684924-v", "00339934-v", "01992503-v", "00781000-v", "01526605-v"] # go on
	,"run_v_out_rel": ["00561571-v", "02071457-v", "02011040-v", "02684784-v", "02069888-v", "00561714-v", "00560247-v", "00099517-v"] # run out
	,"seal_v_in_rel": ["01348013-v"] # seal in
	,"kick_v_up_rel": ["00437321-n", "01371651-v", "01646866-v"] # kick up
	,"run_v_out-of_rel": ["00561571-v", "02071457-v", "02011040-v", "02684784-v", "02069888-v", "00561714-v", "00560247-v", "00099517-v"] # run out
	,"hole_v_up_rel": ["02146525-v", "01113264-v", "00015946-v"] # hole up
	,"shut_v_up_rel": ["01041061-v", "01347678-v", "00461493-v", "00558951-s"] # shut up
	,"filter_v_out_rel": ["01458664-v"] # filter out
	,"chop_v_up_rel": ["01258091-v"] # chop up
	,"round_v_up_rel": ["01381913-v"] # round up
	,"hash_v_out_rel": ["00813978-v"] # hash out
	,"point_v_up_rel": ["01014186-v"] # point up
	,"bottle_v_up_rel": ["02423762-v"] # bottle up
	,"bring_v_about_rel": ["02090679-v", "01752884-v"] # bring about
	,"add_v_up_rel": ["02627363-v", "00949288-v", "02645007-v", "02619612-v"] # add up
	,"go_v_away_rel": ["01848718-v", "02009433-v", "02156546-v", "00426958-v"] # go away
	,"pull_v_in_rel": ["01505254-v", "02289295-v", "02015384-v", "01384439-v"] # pull in
	,"touch_v_down_rel": ["01979702-v"] # touch down
	,"ration_v_out_rel": ["02234803-v"] # ration out
	,"melt_v_down_rel": ["00444629-v"] # melt down
	,"wash_v_out_rel": ["02594833-v", "01535742-v", "01605851-v", "00557686-v", "00542533-v", "00282343-v", "00280112-v"] # wash out
	,"head_v_off_rel": ["02453321-v"] # head off
	,"shack_v_up-with_rel": ["02651193-v"] # shack up
	,"fill_v_out_rel": ["01020731-v", "00172381-v", "02342580-v", "01526956-v", "01194938-v", "00046382-v"] # fill out
	,"strike_v_off_rel": ["00800750-v"] # strike off
	,"blurt_v_out_rel": ["00981944-v"] # blurt out
	,"palm_v_off_rel": ["02244426-v"] # palm off
	,"drive_v_around_rel": ["02058049-v", "02419266-v"] # drive around
	,"throw_v_up_rel": ["00076400-v"] # throw up
	,"sound_v_out_rel": ["00978549-v", "00809071-v"] # sound out
	,"knock_v_out_rel": ["00472426-v", "01414088-v", "00180602-v", "01809980-v", "00451153-v"] # knock out
	,"run_v_over_rel": ["00106960-v", "02072159-v"] # run over
	,"stop_v_over_rel": ["02652922-v", "01862918-v"] # stop over
	,"clown_v_around_rel": ["00105778-v"] # clown around
	,"tease_v_apart_rel": ["01463792-v"] # tease apart
	,"kill_v_off_rel": ["01327582-v"] # kill off
	,"shrug_v_off_rel": ["00742149-v"] # shrug off
	,"conjure_v_up_rel": ["01629958-v"] # conjure up
	,"sign_v_on_rel": ["02409941-v"] # sign on
	,"sober_v_up_rel": ["00149118-v", "00149296-v"] # sober up
	,"blow_v_up_rel": ["00306723-v", "00240293-v", "01795428-v", "00956405-v", "00306298-v", "00264386-v", "00264034-v", "00263682-v"] # blow up
	,"haul_v_up_rel": ["01863158-v"] # haul up
	,"eke_v_out_rel": ["02342580-v", "02616236-v", "02239997-v", "02239846-v"] # eke out
	,"slam_v_on_rel": ["01364997-v"] # slam on
	,"take_v_back_rel": ["02078294-v", "02205887-v", "02458405-v", "01852591-v", "00799076-v", "00610770-v"] # take back
	,"roll_v_down_rel": ["01966706-v"] # roll down
	,"flesh_v_out_rel": ["01194938-v", "00955601-v", "00046382-v"] # flesh out
	,"drag_v_out_rel": ["02705428-v", "00341757-v"] # drag out
	,"make_v_up-of_rel": ["02620587-v", "01753465-v", "02253456-v", "02520730-v", "01634424-v", "00276068-v", "02672540-v", "00764902-v", "00040928-v"] # make up
	,"close_v_out_rel": ["02629390-v", "02352538-v", "00351719-v"] # close out
	,"swear_v_in_rel": ["01017501-v"] # swear in
	,"dole_v_out_rel": ["02294436-v"] # dole out
	,"tick_v_off_rel": ["00662182-v"] # tick off
	,"steal_v_away_rel": ["02076027-v"] # steal away
	,"lay_v_up_rel": ["00512482-v"] # lay up
	,"stick_v_in_rel": ["01025602-v", "00187526-v"] # stick in
	,"glaze_v_over_rel": ["02158034-v", "00125447-v"] # glaze over
	,"blow_v_out_rel": ["00435294-v", "02761897-v", "02761012-v"] # blow out
	,"cut_v_up_rel": ["01255967-v", "00292672-v", "00483801-v", "00201618-v", "00661819-s"] # cut up
	,"raise_v_up_rel": ["01419473-v"] # raise up
	,"call_v_off_rel": ["02477755-v", "01899017-v"] # call off
	,"pull_v_over_rel": ["01841591-v"] # pull over
	,"brush_v_off_rel": ["00800930-v"] # brush off
	,"smooth_v_out_rel": ["02313098-v"] # smooth out
	,"stand_v_up_rel": ["01983264-v", "01117086-v", "01546768-v", "01546111-v", "00895641-v", "02618688-v", "01983597-v"] # stand up
	,"take_v_in_rel": ["02656995-v", "00854904-v", "02765464-v", "02492584-v", "02218173-v", "02150948-v", "01470225-v", "01214786-v", "00602255-v", "02289295-v", "02189168-v", "01540844-v", "01539063-v", "01197980-v", "01156834-v", "00413195-v", "00304100-v"] # take in
	,"save_v_up_rel": ["02265979-v"] # save up
	,"send_v_back_rel": ["00949974-v"] # send back
	,"mess_v_up_rel": ["02527651-v", "01387493-v", "00276214-v"] # mess up
	,"sink_v_in_rel": ["00591755-v", "01457954-v"] # sink in
	,"pipe_v_up_rel": ["01050565-v", "00914420-v"] # pipe up
	,"knock_v_up_rel": ["00053159-v"] # knock up
	,"show_v_off_rel": ["02141973-v"] # show off
	,"finish_v_up_rel": ["00484892-v", "00352558-v"] # finish up
	,"come_v_in_rel": ["02016523-v", "02006709-v", "02667419-v", "00914769-v", "00659776-v"] # come in
	,"suck_v_out_rel": ["01540693-v"] # suck out
	,"double_v_up_rel": ["02063309-v", "02295717-v", "01139623-v"] # double up
	,"yield_v_up_rel": ["02235549-v"] # yield up
	,"switch_v_on_rel": ["01510399-v"] # switch on
	,"air_v_out_rel": ["02112891-v", "00488770-v"] # air out
	,"lift_v_off_rel": ["02014553-v"] # lift off
	,"buck_v_up_rel": ["01806407-v"] # buck up
	,"winnow_v_out_rel": ["00685419-v"] # winnow out
	,"back_v_out_rel": ["01997376-v", "00799383-v"] # back out
	,"pass_v_off_rel": ["02134492-v", "00801522-v", "02052965-v", "00421691-v", "00339934-v", "00105333-v"] # pass off
	,"comb_v_out_rel": ["02223630-v", "00038365-v"] # comb out
	,"toss_v_away_rel": ["02222318-v"] # toss away
	,"speed_v_up_rel": ["00438178-v", "00439343-v"] # speed up
	,"touch_v_off_rel": ["01643657-v"] # touch off
	,"rip_v_up_rel": ["01573891-v"] # rip up
	,"cast_v_out_rel": ["02504017-v", "02222318-v"] # cast out
	,"bite_v_off_rel": ["01445756-v"] # bite off
	,"choke_v_up_rel": ["01479333-v"] # choke up
	,"burn_v_down_rel": ["00377351-v", "00378664-v"] # burn down
	,"bum_v_around_rel": ["02639606-v"] # bum around
	,"weigh_v_down_rel": ["01814266-v", "01597096-v"] # weigh down
	,"go_v_through_rel": ["02110220-v", "01161947-v", "02050132-v", "01197014-v", "00486018-v"] # go through
	,"wear_v_away_rel": ["01552390-v", "01254324-v", "00275253-v"] # wear away
	,"dream_v_up_rel": ["01634142-v"] # dream up
	,"slow_v_up_rel": ["00440580-v", "00440786-v", "00439958-v"] # slow up
	,"pull_v_out_rel": ["02015168-v", "01995211-v", "01351170-v", "02380980-v"] # pull out
	,"ground_v_out_rel": ["01402173-v"] # ground out
	,"pick_v_out_rel": ["00674607-v", "02193194-v"] # pick out
	,"chase_v_away_rel": ["02002720-v"] # chase away
	,"take_v_aback_rel": ["01809064-v"] # take aback
	,"find_v_out_rel": ["00918872-v", "00598954-v", "00920336-v", "00731574-v"] # find out
	,"eat_v_up_rel": ["01196802-v", "01157517-v", "01582409-v"] # eat up
	,"stave_v_off_rel": ["02453321-v"] # stave off
	,"do_v_up_rel": ["01283611-v", "00043078-v"] # do up
	,"snatch_v_up_rel": ["01439745-v"] # snatch up
	,"rein_v_in_rel": ["01862090-v", "02442737-v", "01858362-v"] # rein in
	,"lay_v_off_rel": ["02680814-v", "02403537-v"] # lay off
	,"stub_v_out_rel": ["00478682-v"] # stub out
	,"blank_v_out_rel": ["00609100-v", "00202089-v"] # blank out
	,"split_v_up_rel": ["00439043-n", "02490634-v", "02467662-v", "02431320-v", "00334186-v"] # split up
	,"pass_v_up_rel": ["02237338-v", "02119353-v"] # pass up
	,"go_v_off_rel": ["02073714-v", "00307295-v", "01134238-v", "01526792-v", "00343898-v", "00305846-v"] # go off
	,"let_v_in_rel": ["02449847-v", "02502536-v"] # let in
	,"turn_v_off_rel": ["01510576-v", "01908658-v", "01808626-v"] # turn off
	,"buy_v_back_rel": ["02207890-v"] # buy back
	,"spirit_v_away_rel": ["01435000-v", "01432914-v"] # spirit away
	,"chip_v_in_rel": ["02308741-v"] # chip in
	,"let_v_out_rel": ["00983824-v", "00933821-v", "01475301-v", "00303940-v"] # let out
	,"measure_v_up_rel": ["02679012-v"] # measure up
	,"crack_v_up_rel": ["01785579-v", "00861333-v", "00030366-v"] # crack up
	,"write_v_off_rel": ["00593363-v", "01700540-v", "02477655-v", "00315956-v"] # write off
	,"cotton_v_on_rel": ["00590366-v"] # cotton on
	,"cheer_v_up_rel": ["00859325-v", "00859153-v"] # cheer up
	,"wash_v_away_rel": ["00571273-v", "00557686-v"] # wash away
	,"buy_v_out_rel": ["02274299-v"] # buy out
	,"bust_v_up_rel": ["01566185-v"] # bust up
	,"gouge_v_out_rel": ["01281343-v"] # gouge out
	,"cool_v_down_rel": ["00370412-v", "00370126-v", "00369864-v"] # cool down
	,"call_v_forth_rel": ["01646866-v", "01629958-v"] # call forth
	,"shoot_v_down_rel": ["02055267-v", "01981279-v", "02473688-v"] # shoot down
	,"opt_v_out_rel": ["00679715-v"] # opt out
	,"vomit_v_up_rel": ["00076400-v"] # vomit up
	,"pick_v_up_rel": ["01976089-v", "01207402-v", "01957107-v", "02305586-v", "00598954-v", "02355410-v", "01215137-v", "02287041-v", "02107248-v", "00513757-v", "02486534-v", "01811736-v", "00205598-v", "02117955-v", "01173813-v", "00023473-v"] # pick up
	,"spin_v_around_rel": ["02046755-v"] # spin around
	,"separate_v_out_rel": ["01458664-v"] # separate out
	,"drift_v_off_rel": ["00017282-v"] # drift off
	,"cross_v_off_rel": ["00800750-v"] # cross off
	,"deck_v_out_rel": ["00044149-v"] # deck out
	,"slough_v_off_rel": ["02222846-v", "01254912-v"] # slough off
	,"lock_v_in_rel": ["01348013-v", "01347678-v"] # lock in
	,"chime_v_in_rel": ["00780191-v"] # chime in
	,"give_v_off_rel": ["02631005-v", "02767308-v"] # give off
	,"make_v_out_rel": ["02193194-v", "01064799-v", "00626300-v", "02617567-v", "02587532-v", "01426397-v", "01426153-v", "01020731-v", "00931085-v", "00757056-v"] # make out
	,"cut_v_short_rel": ["00362805-v", "00520602-v", "00317241-v", "00292877-v"] # cut short
	,"spark_v_off_rel": ["01643657-v"] # spark off
	,"slap_v_on_rel": ["01364997-v"] # slap on
	,"set_v_out_rel": ["00345761-v", "01474209-v", "02014165-v"] # set out
	,"add_v_on_rel": ["00183757-v", "01328705-v"] # add on
	,"back_v_away_rel": ["00799383-v"] # back away
	,"check_v_up-on_rel": ["00661824-v"] # check up on
	,"burn_v_off_rel": ["01205000-v", "00196252-v"] # burn off
	,"lift_v_up_rel": ["01976089-v", "01811736-v"] # lift up
	,"move_v_on_rel": ["01992503-v"] # move on
	,"sack_v_out_rel": ["00017865-v"] # sack out
	,"put_v_down_rel": ["01500372-v", "01544692-v", "01981036-v", "01800422-v", "01489465-v", "01326528-v", "01020356-v", "01000214-v"] # put down
	,"lop_v_off_rel": ["01299268-v"] # lop off
	,"put_v_off_rel": ["02642814-v", "01808626-v", "01819387-v", "01790739-v", "00809654-v"] # put off
	,"hang_v_around_rel": ["02639075-v"] # hang around
	,"pull_v_down_rel": ["01661804-v", "01239862-v"] # pull down
	,"play_v_up_rel": ["00514069-v", "01804753-v"] # play up
	,"chat_v_up_rel": ["01037910-v", "00767807-v"] # chat up
	,"eat_v_out_rel": ["01167640-v"] # eat out
	,"reach_v_out_rel": ["01440139-v", "02690093-v", "00744572-v"] # reach out
	,"come_v_back_rel": ["00548153-v", "00959524-v", "01998982-v", "00816353-v"] # come back
	,"leave_v_behind_rel": ["02081578-v", "00360092-v", "00136991-v"] # leave behind
	,"gang_v_up_rel": ["01089737-v"] # gang up
	,"phase_v_in_rel": ["01642717-v"] # phase in
	,"rub_v_out_rel": ["01548718-v"] # rub out
	,"tuck_v_in_rel": ["01173208-v"] # tuck in
	,"do_v_in_rel": ["01327301-v"] # do in
	,"wash_v_down_rel": ["01167290-v", "00455079-v"] # wash down
	,"catch_v_up_rel": ["01998793-v", "00598753-v"] # catch up
	,"water_v_down_rel": ["00488301-v", "00488175-v"] # water down
	,"bail_v_out_rel": ["02494259-v", "00449426-v"] # bail out
	,"fuck_v_off_rel": ["02639606-v", "02010864-v", "01430633-v"] # fuck off
	,"start_v_up_rel": ["01857717-v", "01650610-v"] # start up
	,"auction_v_off_rel": ["02244773-v"] # auction off
	,"bounce_v_back_rel": ["00268011-v"] # bounce back
	,"pop_v_up_rel": ["02157519-v"] # pop up
	,"tire_v_out_rel": ["00075021-v"] # tire out
	,"drive_v_out_rel": ["02002720-v", "02056466-v", "00576228-v"] # drive out
	,"stamp_v_out_rel": ["00355038-v"] # stamp out
	,"beef_v_up_rel": ["00220869-v"] # beef up
	,"spruce_v_up_rel": ["00293977-v", "00043278-v"] # spruce up
	,"fritter_v_away_rel": ["01195804-v"] # fritter away
	,"pass_v_along_rel": ["00742320-v"] # pass along
	,"book_v_up_rel": ["00794880-v"] # book up
	,"cancel_v_out_rel": ["00471196-v"] # cancel out
	,"show_v_up_rel": ["00423702-v", "02139544-v"] # show up
	,"spin_v_off_rel": ["00345184-v"] # spin off
	,"even_v_out_rel": ["02672540-v", "01307142-v", "00416880-v", "00416705-v"] # even out
	,"count_v_out_rel": ["01101313-v"] # count out
	,"map_v_out_rel": ["01756149-v"] # map out
	,"break_v_out_rel": ["00345508-v", "00346958-v", "02073233-v", "01485732-v", "00309074-v"] # break out
	,"fight_v_back_rel": ["01092284-v", "01091427-v"] # fight back
	,"boot_v_out_rel": ["02401809-v", "01468576-v"] # boot out
	,"drive_v_in_rel": ["01113620-v", "01980300-v", "01352996-v"] # drive in
	,"pile_v_up_rel": ["00158804-v", "01504298-v", "02304982-v"] # pile up
	,"drop_v_by_rel": ["02488641-v"] # drop by
	,"pull_v_away_rel": ["01994442-v"] # pull away
	,"heat_v_up_rel": ["00372665-v", "00371264-v", "00227667-v"] # heat up
	,"sit_v_down_rel": ["01984902-v", "01543998-v", "01543123-v"] # sit down
	,"sit_v_out_rel": ["02726543-v", "00670179-v"] # sit out
	,"turn_v_on_rel": ["01510399-v", "02711987-v", "02141414-v", "00548479-v", "01762528-v", "01762283-v", "01200934-v"] # turn on
	,"hold_v_on_rel": ["01216004-v", "00362610-v", "00350461-v", "00790509-v", "02202384-v"] # hold on
	,"pitch_v_in_rel": ["01173057-v"] # pitch in
	,"shore_v_up_rel": ["01219004-v"] # shore up
	,"fence_v_in_rel": ["01588134-v", "01130607-v"] # fence in
	,"drum_v_up_rel": ["01385643-v"] # drum up
	,"drag_v_on_rel": ["02705428-v", "00341757-v"] # drag on
	,"blot_v_out_rel": ["00313987-v"] # blot out
	,"keel_v_over_rel": ["01976702-v"] # keel over
	,"cut_v_off_rel": ["00778275-v", "00292507-v", "01299268-v", "01440646-v", "01259458-v", "01254692-v", "00662318-s"] # cut off
	,"wear_v_thin_rel": ["00469382-v"] # wear thin
	,"weed_v_out_rel": ["02223630-v"] # weed out
	,"buoy_v_up_rel": ["00860136-v", "01814074-v", "01218512-v"] # buoy up
	,"gobble_v_up_rel": ["01174099-v"] # gobble up
	,"look_v_up-dir_rel": ["00877083-v"] # look up
	,"come_v_along_rel": ["00425071-v", "00248659-v"] # come along
	,"get_v_around_rel": ["00935987-v", "00811171-v", "02389815-v", "01842888-v"] # get around
	,"pass_v_out_rel": ["00023646-v", "02201644-v", "00023868-v"] # pass out
	,"pipe_v_down_rel": ["02190188-v"] # pipe down
	,"gas_v_up_rel": ["02338629-v"] # gas up
	,"send_v_around_rel": ["02043501-v"] # send around
	,"come_v_through_rel": ["00426749-v", "02021921-v", "02619924-v", "02524171-v"] # come through
	,"spin_v_out_rel": ["00318706-v"] # spin out
	,"put_v_back_rel": ["01308381-v", "02702674-v"] # put back
	,"put_v_out_rel": ["02507736-v", "01625532-v", "01569017-v", "00027705-v", "02760495-v", "02755452-v", "01615457-v", "01154382-v", "00967625-v", "00021065-v"] # put out
	,"string_v_together_rel": ["04337974-n", "02880546-n", "04338143-n", "08459648-n", "07013549-n", "03235560-n", "14867365-n", "09449282-n", "04338359-n", "02999757-n", "01359432-v", "00190389-v", "01993805-v", "01360571-v", "01360423-v", "01360316-v", "01359145-v"] # string
	,"pin_v_down_rel": ["00715541-v", "02496185-v", "01340149-v"] # pin down
	,"grow_v_over_rel": ["00232714-v"] # grow over
	,"tense_v_up_rel": ["00026153-v", "00025203-v"] # tense up
	,"jack_v_up_rel": ["01219544-v"] # jack up
	,"clutter_v_up_rel": ["00181875-v"] # clutter up
	,"hollow_v_out_rel": ["01282545-v"] # hollow out
	,"drag_v_down_rel": ["01597096-v"] # drag down
	,"thrash_v_out_rel": ["01064151-v"] # thrash out
	,"set_v_forth_rel": ["01001294-v", "02014165-v"] # set forth
	,"sleep_v_off_rel": ["02288042-v"] # sleep off
	,"fly_v_on_rel": ["01941006-v"] # fly on
	,"ring_v_up_rel": ["04981658-n", "13875392-n", "03533972-n", "09246883-n", "08244062-n", "07391863-n", "04092959-n", "04092609-n", "02785191-n", "02180898-v", "02183787-v", "02181538-v", "00789448-v", "01467370-v", "01297401-v"] # ring
	,"box_v_up_rel": ["02711721-v"] # box up
	,"strike_v_up_rel": ["01651110-v", "01642311-v"] # strike up
	,"pay_v_up_rel": ["02252931-v"] # pay up
	,"look_v_up_rel": ["00877083-v"] # look up
	,"speak_v_up_rel": ["01027668-v", "00916123-v"] # speak up
	,"feed_v_in_rel": ["00189511-v"] # feed in
	,"trot_v_out_rel": ["02143906-v"] # trot out
	,"sum_v_up_rel": ["01007924-v", "02752695-v", "00949288-v"] # sum up
	,"tighten_v_up_rel": ["00418765-v"] # tighten up
	,"come_v_around_rel": ["00654446-v", "00344042-v"] # come around
	,"drop_v_out_rel": ["01083044-v", "02383174-v", "02382938-v"] # drop out
	,"sweep_v_away_rel": ["01621219-v", "01770370-v"] # sweep away
	,"pass_v_on_rel": ["02230772-v", "02296153-v", "01992503-v", "02230247-v", "02589013-v", "02043190-v", "00742320-v"] # pass on
	,"tie_v_up_rel": ["01286913-v", "02271923-v", "01477014-v", "01305542-v", "01286038-v"] # tie up
	,"patch_v_up_rel": ["00262703-v", "00764902-v"] # patch up
	,"tidy_v_up_rel": ["00275843-v"] # tidy up
	,"jot_v_down_rel": ["01006056-v"] # jot down
	,"finish_v_off_rel": ["00484892-v"] # finish off
	,"mark_v_off_rel": ["00234725-v", "00662182-v"] # mark off
	,"mark_v_out_rel": ["00234725-v"] # mark out
	,"lift_v_out_rel": ["01312371-v"] # lift out
	,"wear_v_out_rel": ["00075021-v", "01369346-v", "00469382-v"] # wear out
	,"cash_v_in_rel": ["02256354-v"] # cash in
	,"string_v_along_rel": ["04337974-n", "02880546-n", "04338143-n", "08459648-n", "07013549-n", "03235560-n", "14867365-n", "09449282-n", "04338359-n", "02999757-n", "01359432-v", "00190389-v", "01993805-v", "01360571-v", "01360423-v", "01360316-v", "01359145-v"] # string
	,"turn_v_over_rel": ["02230772-v", "01909978-v", "01866192-v", "01309701-v", "02261256-v", "02089420-v", "01909397-v", "01222958-v", "00813044-v"] # turn over
	,"pull_v_off_rel": ["01592456-v", "02404467-v", "02522864-v", "01592774-v"] # pull off
	,"pin_v_up_rel": ["01340149-v"] # pin up
	,"help_v_out_rel": ["02548422-v"] # help out
	,"scare_v_away_rel": ["01785748-v"] # scare away
	,"iron_v_out_rel": ["00208055-v", "01390833-v"] # iron out
	,"tune_v_in_rel": ["02171514-v"] # tune in
	,"knock_v_down_rel": ["01239862-v", "01412346-v", "00336158-v"] # knock down
	,"talk_v_over_rel": ["00813978-v"] # talk over
	,"pare_v_down_rel": ["00233089-v"] # pare down
	,"cut_v_back_rel": ["02004701-v", "00429060-v", "01321002-v", "00236592-v"] # cut back
	,"slim_v_down_rel": ["00045817-v"] # slim down
	,"usher_v_in_rel": ["00349592-v"] # usher in
	,"die_v_out_rel": ["00427683-v", "01555034-v"] # die out
	,"bring_v_home_rel": ["00543161-v", "02289854-v"] # bring home
	,"snap_v_up_rel": ["02304648-v"] # snap up
	,"cave_v_in_rel": ["07361416-n", "01989053-v"] # cave in
	,"scale_v_down_rel": ["00428247-v", "00240131-v"] # scale down
	,"wall_v_in_rel": ["01389942-v"] # wall in
	,"lock_v_out_rel": ["02449717-v"] # lock out
	,"ward_v_off_rel": ["02453321-v", "01129591-v"] # ward off
	,"home_v_in_rel": ["01153007-v"] # home in
	,"polish_v_up_rel": ["00473799-v"] # polish up
	,"swallow_v_up_rel": ["01582409-v"] # swallow up
	,"draw_v_away_rel": ["01999688-v", "01592774-v"] # draw away
	,"tack_v_on_rel": ["01328513-v"] # tack on
	,"stir_v_up_rel": ["02585050-v", "01761120-v", "01419473-v", "00851239-v"] # stir up
	,"size_v_up_rel": ["02153387-v"] # size up
	,"log_v_on_rel": ["02249147-v"] # log on
	,"tote_v_up_rel": ["00949288-v"] # tote up
	,"spit_v_out_rel": ["00102303-v", "01045318-v", "00006238-v"] # spit out
	,"chew_v_out_rel": ["00824767-v"] # chew out
	,"firm_v_up_rel": ["01021871-v"] # firm up
	,"bowl_v_over_rel": ["01909978-v", "00726153-v"] # bowl over
	,"get_v_off_rel": ["02016062-v", "02412089-v", "01062555-v", "00905059-v", "00810729-v", "02197250-v", "01958452-v", "01923732-v", "01437888-v", "01200934-v", "00941855-v"] # get off
	,"win_v_over_rel": ["00769553-v"] # win over
	,"spring_v_up_rel": ["02624263-v"] # spring up
	,"band_v_together_rel": ["02470685-v"] # band together
	,"carry_v_out_rel": ["01640855-v", "00486018-v"] # carry out
	,"rack_v_up_rel": ["01111816-v", "01499849-v", "01102997-v", "00452394-v"] # rack up
	,"tear_v_apart_rel": ["00846344-v"] # tear apart
	,"push_v_down_rel": ["01239862-v"] # push down
	,"buy_v_off_rel": ["02284803-v"] # buy off
	,"knuckle_v_under_rel": ["00804476-v"] # knuckle under
	,"screen_v_out_rel": ["02400378-v"] # screen out
	,"snuff_v_out_rel": ["00478217-v", "02761897-v"] # snuff out
	,"drop_v_off_rel": ["00152887-v", "00017282-v", "01489465-v", "01113806-v", "00204391-v"] # drop off
	,"scoop_v_up_rel": ["01312371-v"] # scoop up
	,"charge_v_up_rel": ["01762528-v"] # charge up
	,"spell_v_out_rel": ["01005904-v", "01700149-v", "00937879-v"] # spell out
	,"clear_v_off_rel": ["00181559-v"] # clear off
	,"move_v_in_rel": ["01856096-v", "02015384-v", "01855982-v"] # move in
	,"hook_v_up_rel": ["02488834-v"] # hook up with
	,"plug_v_in_rel": ["01421122-v"] # plug in
	,"chop_v_down_rel": ["01257507-v"] # chop down
	,"run_v_around_rel": ["01883716-v"] # run around
	,"bottom_v_out_rel": ["02007898-v", "01238500-v"] # bottom out
	,"close_v_up_rel": ["02426395-v", "01476483-v", "01291941-v", "01041061-v", "00410043-r"] # close up
	,"keep_v_on_rel": ["13365286-n", "03610098-n", "03525252-n", "02681795-v", "02684924-v", "02202384-v", "02450505-v", "02578872-v", "00732552-v", "02202928-v", "01065877-v", "02651853-v", "02410175-v", "01184625-v", "02734800-v", "02578510-v", "02422663-v", "02733122-v", "02652016-v", "02283716-v", "02204094-v", "02203844-v", "02203168-v", "01302019-v", "00212414-v"] # keep
	,"bring_v_out_rel": ["02143283-v", "01475301-v", "00967625-v", "00514463-v", "02157100-v", "01818669-v", "01214597-v", "01065115-v", "00933821-v"] # bring out
	,"drop_v_in_rel": ["02488641-v"] # drop in
	,"hose_v_down_rel": ["00228521-v"] # hose down
	,"set_v_aside_rel": ["00724150-v", "00542668-v"] # set aside
	,"parcel_v_out_rel": ["02294436-v"] # parcel out
	,"crop_v_up_rel": ["02157519-v"] # crop up
	,"clear_v_up_rel": ["00939857-v", "00484892-v", "00178235-v", "02771169-v", "00621058-v"] # clear up
	,"give_v_out_rel": ["02767308-v", "02201644-v", "00560247-v", "00434374-v"] # give out
	,"leave_v_out_rel": ["00615774-v", "00614999-v"] # leave out
	,"open_v_up_rel": ["01346003-v", "00540101-v", "00539936-v", "01645421-v", "02426171-v", "01346804-v", "01041298-v"] # open up
	,"clear_v_out_rel": ["01856350-v", "00576228-v", "00448864-v"] # clear out
	,"strip_v_down_rel": ["00049900-v"] # strip down
	,"live_v_out_rel": ["02619020-v", "01177505-v"] # live out
	,"hand_v_down_rel": ["02230615-v"] # hand down
	,"set_v_up_rel": ["02427103-v", "01656788-v", "01661243-v", "00407848-v", "01463963-v", "01661472-v", "02578008-v", "01642924-v", "01569566-v", "01570108-v", "02573127-v", "01514126-v", "00735571-v", "00408085-v", "00406243-v"] # set up
	,"watch_v_out_rel": ["02151966-v"] # watch out
	,"mull_v_over_rel": ["00630380-v"] # mull over
	,"bring_v_up_rel": ["01629958-v", "02539788-v", "02398161-v", "01974062-v", "01859854-v", "01025246-v", "01024190-v", "00098346-v"] # bring up
	,"back_v_down_rel": ["01997680-v", "02380980-v"] # back down
	,"round_v_down_rel": ["00145623-v"] # round down
	,"call_v_back_rel": ["02312478-v", "00607780-v", "00791764-v", "00791506-v"] # call back
	,"kick_v_off_rel": ["02395782-v"] # kick off
	,"knock_v_off_rel": ["01327301-v", "02349597-v", "02322230-v", "01700655-v", "00363110-v"] # knock off
	,"tell_v_off_rel": ["00825648-v"] # tell off
	,"hold_v_down_rel": ["02283608-v", "00235763-v"] # hold down
	,"ferret_v_out_rel": ["00722065-v"] # ferret out
	,"top_v_off_rel": ["00484712-v", "00453294-v"] # top off
	,"haul_v_away_rel": ["01451665-v"] # haul away
	,"boil_v_down-to_rel": ["00237704-v", "00237259-v", "00236999-v"] # boil down
	,"bear_v_out_rel": ["02663340-v"] # bear out
	,"freak_v_out_rel": ["05898430-n", "01784148-v"] # freak out
	,"chalk_v_up_rel": ["02321245-v", "00949841-v"] # chalk up
	,"wipe_v_off_rel": ["01392918-v", "01548718-v"] # wipe off
	,"sort_v_out_rel": ["00654625-v", "00621058-v", "02553428-v"] # sort out
	,"turn_v_out_rel": ["02633881-v", "02634133-v", "01623792-v", "02610845-v", "00425522-v", "01652139-v", "01468576-v", "02429475-v", "02340360-v", "02045415-v", "01510576-v", "00018158-v"] # turn out
	,"cry_v_out_rel": ["00912048-v"] # cry out
	,"go_v_ahead_rel": ["00781303-v"] # go ahead
	,"copy_v_out_rel": ["01747602-v"] # copy out
	,"fall_v_back_rel": ["02039315-v", "01997862-v", "01904120-v", "01113806-v", "02590072-v", "00093327-v"] # fall back
	,"carry_v_on_rel": ["02445509-v", "02679899-v", "00781000-v", "02517655-v"] # carry on
	,"track_v_down_rel": ["01143838-v"] # track down
	,"get_v_on_rel": ["02458566-v"] # get on with
	,"play_v_down_rel": ["00513492-v"] # play down
	,"pop_v_out_rel": ["00426156-v", "02081946-v", "01920457-v", "00529411-v"] # pop out
	,"draw_v_back_rel": ["01994442-v", "01609773-v"] # draw back
	,"tip_v_off_rel": ["00873469-v"] # tip off
	,"kick_v_around_rel": ["02604305-v", "02516978-v", "00813651-v"] # kick around
	,"silt_v_up_rel": ["01479545-v"] # silt up
	,"boil_v_down_rel": ["00237704-v", "00237259-v", "00236999-v"] # boil down
	,"screw_v_up_rel": ["00227667-v", "02527651-v", "01353311-v", "00034634-v"] # screw up
	,"keep_v_up_rel": ["01113975-v", "02679530-v", "02280132-v", "00118764-v", "00020449-v"] # keep up
	,"get_v_along_rel": ["02617567-v", "02458566-v", "00248659-v"] # get along
	,"sniff_v_out_rel": ["02125460-v"] # sniff out
	,"pull_v_up_rel": ["01863158-v", "01982686-v", "01863410-v", "01351170-v"] # pull up
	,"rabbit_v_on_rel": ["01051956-v"] # rabbit on
	,"shake_v_off_rel": ["02073545-v", "01513430-v"] # shake off
	,"hook_v_up_rel": ["01366426-v"] # hook up
	,"take_v_down_rel": ["01973125-v", "01800422-v", "01661804-v", "01020934-v"] # take down
	,"send_v_in_rel": ["01437597-v", "02488168-v"] # send in
	,"look_v_around_rel": ["02132420-v"] # look around
	,"kick_v_out_rel": ["02501738-v", "02401809-v"] # kick out
	,"hang_v_on_rel": ["01328513-v", "00350461-v", "00790509-v"] # hang on
	,"set_v_apart_rel": ["00677683-v", "00495808-v"] # set apart
	,"factor_v_out_rel": ["00640650-v", "00640385-v"] # factor out
	,"black_v_out_rel": ["02762299-v", "00312648-v", "00201906-v", "00023868-v"] # black out
	,"start_v_out_rel": ["00345761-v", "02014165-v"] # start out
	,"squirrel_v_away_rel": ["02305856-v"] # squirrel away
	,"cart_v_away_rel": ["01451665-v"] # cart away
	,"lash_v_out_rel": ["00862683-v"] # lash out
	,"let_v_up_rel": ["00245059-v", "00156276-v"] # let up
	,"narrow_v_down_rel": ["00715541-v", "00437449-v"] # narrow down
	,"nod_v_off_rel": ["00017282-v"] # nod off
	,"cut_v_in_rel": ["02295447-v", "02057878-v", "00780191-v", "00520194-v", "00396234-v"] # cut in
	,"suck_v_up_rel": ["01539063-v", "01804753-v", "00880978-v"] # suck up
	,"bring_v_down_rel": ["01973125-v", "02402409-v", "00748282-v", "01981036-v", "01830307-v", "00429060-v"] # bring down
	,"set_v_out-aim_rel": ["00345761-v", "01474209-v", "02014165-v"] # set out
	,"square_v_away_rel": ["00275843-v"] # square away
	,"give_v_away_rel": ["02201855-v", "00933821-v", "02293915-v", "00841986-v"] # give away
	,"brush_v_aside_rel": ["00800930-v"] # brush aside
	,"sign_v_up_rel": ["02409941-v", "01097309-v"] # sign up
	,"stink_v_up_rel": ["02126022-v"] # stink up
	,"dry_v_out_rel": ["00219403-v", "02771756-v", "00218475-v"] # dry out
	,"swell_v_up_rel": ["00256507-v"] # swell up
	,"clean_v_out_rel": ["00448864-v", "02403408-v", "02314784-v"] # clean out
	,"strike_v_down_rel": ["02477334-v", "01325934-v", "01258302-v"] # strike down
	,"gear_v_up_rel": ["00406243-v"] # gear up
	,"run_v_up_rel": ["00159553-v", "01455754-v", "01329239-v", "02321245-v", "01666604-v"] # run up
	,"shell_v_out_rel": ["02294436-v"] # shell out
	,"think_v_up_rel": ["01634142-v"] # think up
	,"frighten_v_off_rel": ["01785748-v"] # frighten off
	,"thrust_v_out_rel": ["01873157-v"] # thrust out
	,"flag_v_down_rel": ["01860620-v"] # flag down
	,"come_v_out_rel": ["00423702-v", "00425967-v", "00528990-v", "02610845-v", "02097925-v", "00659776-v", "02089174-v", "02081946-v", "00935456-v", "00935141-v", "00548266-v"] # come out
	,"pull_v_back_rel": ["01994442-v", "01609773-v", "01449053-v", "01243298-v", "00799383-v"] # pull back
	,"push_v_through_rel": ["00548266-v"] # push through
	,"end_v_up_rel": ["00352558-v"] # end up
	,"date_v_back_rel": ["02723951-v"] # date back
	,"swoop_v_up_rel": ["01440010-v"] # swoop up
	,"light_v_up_rel": ["02761229-v", "00291873-v", "02771169-v", "02764122-v", "01199881-v"] # light up
	,"well_v_up_rel": ["02626405-v"] # well up
	,"lay_v_out_rel": ["01474209-v", "00407848-v", "02366575-v", "00772967-v", "00711040-v"] # lay out
	,"wear_v_on_rel": ["00432176-v"] # wear on
	,"load_v_up_rel": ["01489989-v"] # load up
	,"pipe_v_in_rel": ["01436391-v", "02080652-v"] # pipe in
	,"coop_v_up_rel": ["01347519-v"] # coop up
	,"hammer_v_out_rel": ["01064151-v"] # hammer out
	,"press_v_on_rel": ["01993549-v"] # press on
	,"turn_v_around_rel": ["07411160-n", "01878949-v", "00206797-v", "00205598-v"] # turn around
	,"let_v_go-of_rel": ["01474550-v"] # let go of
	,"write_v_out_rel": ["01754576-v", "01064799-v"] # write out
	,"queue_v_up_rel": ["02036755-v"] # queue up
	,"fuck_v_up_rel": ["02527651-v"] # fuck up
	,"blast_v_off_rel": ["01515056-v"] # blast off
	,"close_v_in_rel": ["02054703-v", "01587062-v"] # close in
	,"hang_v_out_rel": ["02390287-v"] # hang out
	,"drink_v_down_rel": ["01202374-v"] # drink down
	,"root_v_out_rel": ["01566916-v", "01662118-v"] # root out
	,"dig_v_in_rel": ["01531124-v", "01173057-v"] # dig in
	,"settle_v_down_rel": ["01988458-v", "00415398-v", "01763829-v"] # settle down
	,"die_v_off_rel": ["00427683-v"] # die off
	,"rush_v_out_rel": ["01966501-v"] # rush out
	,"clear_v_away_rel": ["00181559-v"] # clear away
	,"link_v_up_rel": ["02622234-v", "01354673-v", "00713167-v"] # link up
	,"shake_v_up_rel": ["01865051-v", "02433123-v", "01890351-v", "01761706-v", "01419473-v", "01391946-v"] # shake up
	,"last_v_out_rel": ["02619122-v"] # last out
	,"cut_v_down_rel": ["00429060-v", "01322675-v", "01239862-v", "01104509-v", "01319562-v", "01258302-v"] # cut down
	,"push_v_away_rel": ["01873294-v"] # push away
	,"free_v_up_rel": ["07947958-n", "02421374-v", "02350175-v", "01528522-v", "02564146-v", "02494047-v", "02422026-v", "01475953-v", "00902424-v", "02316304-v", "01757994-v", "00269682-v", "01061489-a", "01058363-a", "01710260-s", "01624010-s", "01060947-s", "01065694-a", "01624115-s", "00927978-s", "00916199-s", "00358021-r"] # free
	,"slip_v_off_rel": ["00051370-v"] # slip off
	,"finish_v_up_rel": ["04700642-n", "15267536-n", "14459824-n", "08567877-n", "07353376-n", "07333162-n", "07291312-n", "05717747-n", "00210518-n", "00484166-v", "00352558-v", "02609764-v", "01265989-v", "01196802-v", "00351963-v"] # finish
	,"shut_v_off_rel": ["02680531-v", "02031826-v", "01477394-v"] # shut off
	,"sop_v_up_rel": ["01539063-v", "01197980-v"] # sop up
	,"stash_v_away_rel": ["02281093-v"] # stash away
	,"wake_v_up_rel": ["00018813-v", "00018526-v"] # wake up
	,"move_v_up_rel": ["01969779-v", "01968569-v"] # move up
	,"taper_v_off_rel": ["02683671-v", "00305417-v"] # taper off
	,"block_v_off_rel": ["01126961-v", "01478002-v", "01477394-v"] # block off
	,"hitch_v_up_rel": ["01593134-v"] # hitch up
	,"crowd_v_out_rel": ["02013840-v"] # crowd out
	,"bump_v_off_rel": ["02482425-v"] # bump off
	,"straighten_v_up_rel": ["01982686-v"] # straighten up
	,"run_v_off_rel": ["02073714-v", "02011040-v", "02002720-v", "02074186-v", "02067889-v", "01736299-v", "01081505-v"] # run off
	,"look_v_up-to_rel": ["01827858-v"] # look up to
	,"send_v_off_rel": ["01955127-v", "01515791-v", "01062555-v"] # send off
	,"straighten_v_out_rel": ["00208055-v", "01463520-v", "00167934-v", "01368597-v", "00621058-v", "00275843-v"] # straighten out
	,"eat_v_in_rel": ["01167537-v"] # eat in
	,"brick_v_up_rel": ["01390078-v"] # brick up
	,"peel_v_off_rel": ["01263215-v", "00050315-v", "02033703-v", "01259951-v", "00009492-v"] # peel off
	,"stand_v_out_rel": ["02674564-v", "02673965-v", "01932834-v", "01116980-v"] # stand out
	,"boil_v_over_rel": ["00375268-v"] # boil over
	,"fess_v_up_rel": ["00817909-v"] # fess up
	,"mix_v_up_rel": ["01657254-v", "00620379-v"] # mix up
	,"string_v_on_rel": ["04337974-n", "02880546-n", "04338143-n", "08459648-n", "07013549-n", "03235560-n", "14867365-n", "09449282-n", "04338359-n", "02999757-n", "01359432-v", "00190389-v", "01993805-v", "01360571-v", "01360423-v", "01360316-v", "01359145-v"] # string
	,"grind_v_out_rel": ["01753272-v"] # grind out
	,"put_v_up_rel": ["01570403-v", "02376289-v", "01661243-v", "00668099-v", "02297571-v", "00213794-v", "02459173-v", "02237782-v", "00879540-v"] # put up
	,"chop_v_off_rel": ["01299268-v"] # chop off
	,"fight_v_off_rel": ["01131197-v"] # fight off
	,"drink_v_up_rel": ["01175937-v"] # drink up
	,"cook_v_up_rel": ["01666131-v", "01634424-v"] # cook up
	,"snap_v_off_rel": ["01298931-v"] # snap off
	,"bundle_v_up_rel": ["01487008-v", "00047032-v"] # bundle up
	,"roll_v_up_rel": ["00435853-v", "02304982-v", "02006453-v", "01487008-v", "01345589-v", "00435688-v", "00125078-v"] # roll up
	,"wrap_v_up_rel": ["01283208-v", "00484892-v", "00435688-v", "00048633-v"] # wrap up
	,"spread_v_out_rel": ["02060141-v", "01360715-v", "02082690-v", "02077148-v", "02045415-v", "02028994-v", "01579813-v"] # spread out
	,"bone_v_up_rel": ["00605783-v"] # bone up
	,"build_v_in_rel": ["00467151-v"] # build in
	,"break_v_in_rel": ["02570684-v", "00780191-v", "00347804-v", "01207817-v", "00335555-v", "00202569-v"] # break in
	,"fork_v_over_rel": ["02293321-v"] # fork over
	,"write_v_in_rel": ["02461807-v", "00993453-v"] # write in
	,"pony_v_up_rel": ["02200341-v"] # pony up
	,"write_v_up_rel": ["06681551-n", "01068134-v", "01754576-v"] # write up
	,"step_v_out_rel": ["02016401-v"] # step out
	,"round_v_out_rel": ["00485274-v", "00172381-v", "00145623-v", "00145147-v"] # round out
	,"soup_v_up_rel": ["00170997-v"] # soup up
	,"wash_v_up_rel": ["00025034-v", "02080482-v", "01533166-v", "00423257-v", "00075421-v"] # wash up
	,"roll_v_out_rel": ["01391280-v", "01487185-v"] # roll out
	,"cool_v_off_rel": ["01763829-v", "00370126-v", "01777707-v"] # cool off
	,"break_v_open_rel": ["01346430-v", "00309310-v", "00307785-v"] # break open
	,"scare_v_off_rel": ["01785748-v"] # scare off
	,"pick_v_off_rel": ["02484875-v", "01592456-v"] # pick off
	,"take_v_x-off_rel": ["02014165-v", "00179060-v", "02014553-v", "02411950-v", "01743313-v", "00050454-v", "01864438-v", "01326323-v", "00641252-v"] # take off
	,"stretch_v_out_rel": ["02054989-v", "01985271-v", "00027705-v", "00101434-v", "00028167-v"] # stretch out
	,"push_v_forward_rel": ["01996574-v"] # push forward
	,"scoop_v_out_rel": ["01282294-v", "01312371-v"] # scoop out
	,"check_v_out_rel": ["00661824-v", "00966492-v", "02658283-v", "02376833-v", "02363742-v", "02311260-v", "00809071-v"] # check out
	,"make_v_up_rel": ["02620587-v", "01753465-v", "02253456-v", "02520730-v", "01634424-v", "00276068-v", "02672540-v", "00764902-v", "00040928-v"] # make up
	,"turn_v_up_rel": ["00423702-v", "01277974-v", "02286204-v", "02633881-v", "01313923-v"] # turn up
	,"ice_v_over_rel": ["02758581-v"] # ice over
	,"bring_v_forth_rel": ["01627355-v", "02141146-v", "01752495-v", "00054628-v"] # bring forth
	,"polish_v_off_rel": ["00484892-v", "02482425-v", "01196802-v"] # polish off
	,"find_v_out-about_rel": ["00918872-v", "00598954-v", "00920336-v", "00731574-v"] # find out
	,"leave_v_off_rel": ["02684078-v", "00615774-v", "00572661-v"] # leave off
	,"close_v_off_rel": ["02680531-v", "02031826-v", "01477394-v"] # close off
	,"stick_v_around_rel": ["02638444-v", "01857392-v"] # stick around
	,"come_v_across_rel": ["02286687-v", "02136138-v", "02023107-v", "01063529-v", "00592037-v"] # come across
	,"dredge_v_up_rel": ["01025785-v"] # dredge up
	,"hot_v_up_rel": ["00372665-v", "00227667-v", "00170997-v"] # hot up
	,"step_v_up_rel": ["00290302-v", "00439849-v", "02089174-v"] # step up
	,"ball_v_up_rel": ["02527651-v"] # ball up
	,"set_v_in_rel": ["02609439-v", "02769642-v", "00415743-v"] # set in
	,"stick_v_up_rel": ["02277448-v", "00895641-v"] # stick up
	,"shout_v_out_rel": ["00913065-v", "00915265-v"] # shout out
	,"mount_v_up_rel": ["01923414-v"] # mount up
	,"bring_v_forward_rel": ["01993926-v", "01025455-v"] # bring forward
	,"scrape_v_up_rel": ["01384752-v"] # scrape up
	,"hold_v_back_rel": ["01131473-v", "02422663-v", "02726044-v", "02641463-v", "02283324-v", "02146790-v"] # hold back
	,"stand_v_in_rel": ["02258617-v"] # stand in
	,"shape_v_up_rel": ["00248659-v"] # shape up
	,"follow_v_up_rel": ["00486018-v", "00230276-v"] # follow up
	,"freshen_v_up_rel": ["00163441-v", "00024814-v"] # freshen up
	,"clam_v_up_rel": ["01041061-v"] # clam up
	,"work_v_out_rel": ["00251270-v", "02611106-v", "00251463-v", "00099721-v", "00638585-v", "00637259-v", "00634906-v", "00100551-v"] # work out
	,"luck_v_out_rel": ["02524739-v"] # luck out
	,"belt_v_out_rel": ["01704030-v"] # belt out
	,"get_v_around-to_rel": ["00935987-v", "00811171-v", "02389815-v", "01842888-v"] # get around
	,"face_v_up_rel": ["00812298-v"] # face up
	,"look_v_out_rel": ["02151966-v", "01129064-v"] # look out
	,"scrunch_v_up_rel": ["01545314-v", "01278427-v"] # scrunch up
	,"sweat_v_off_rel": ["00046022-v"] # sweat off
	,"work_v_up_rel": ["00252990-v", "00096648-v", "00253277-v", "00251270-v"] # work up
	,"put_v_forward_rel": ["00878136-v", "02373785-v", "01629958-v", "00879540-v"] # put forward
	,"puff_v_up_rel": ["00264578-v", "00263682-v", "02596908-v", "01065272-v"] # puff up
	,"puff_v_out_rel": ["00263682-v"] # puff out
	,"rip_v_off_rel": ["02573275-v"] # rip off
	,"hem_v_in_rel": ["01607716-v", "01127411-v"] # hem in
	,"rough_v_in_rel": ["01754452-v"] # rough in
	,"bang_v_up_rel": ["01566705-v", "00053159-v"] # bang up
	,"kick_v_in_rel": ["02609439-v", "02308741-v", "01586738-v"] # kick in
	,"hang_v_up_rel": ["01309027-v", "01481360-v", "00363003-v"] # hang up
	,"shoo_v_away_rel": ["02003480-v"] # shoo away
	,"sign_v_off_rel": ["00974031-v"] # sign off
	,"get_v_up_rel": ["01983264-v", "00018158-v", "01974062-v", "00018405-v", "00096648-v", "00044149-v", "01651444-v", "00605783-v"] # get up
	,"figure_v_out_rel": ["00634906-v"] # figure out
	,"log_v_in_rel": ["02249147-v"] # log in
	,"whip_v_up_rel": ["01666002-v"] # whip up
	,"shoot_v_up_rel": ["00432572-v"] # shoot up
	,"slice_v_up_rel": ["01254477-v"] # slice up
	,"trim_v_down_rel": ["00429060-v"] # trim down
	,"bed_v_down_rel": ["00017531-v"] # bed down
	,"calm_v_down_rel": ["01763829-v", "01764800-v", "00558061-v"] # calm down
	,"break_v_away_rel": ["02073233-v", "01259691-v", "02535716-v", "02535457-v", "02075049-v"] # break away
	,"turn_v_back_rel": ["02004528-v", "00387310-v", "02002720-v", "01131473-v", "00386715-v"] # turn back
	,"mop_v_up_rel": ["00211110-n", "01393339-v", "01102997-v", "00484892-v"] # mop up
	,"mess_v_around_rel": ["01473346-v"] # mess around
	,"blow_v_off_rel": ["01290945-v"] # blow off
	,"build_v_up_rel": ["00154608-v", "00252990-v", "01087197-v", "00253277-v", "00171852-v"] # build up
	,"mark_v_down_rel": ["02320078-v"] # mark down
	,"haul_v_off_rel": ["01451665-v"] # haul off
	,"trade_v_in_rel": ["02260085-v"] # trade in
	,"drive_v_home_rel": ["02358327-v", "01014362-v"] # drive home
	,"chill_v_out_rel": ["01763829-v"] # chill out
	,"put_v_through_rel": ["00486018-v", "01355906-v"] # put through
	,"hold_v_up_rel": ["01217043-v", "02141559-v", "00459776-v", "02277448-v", "02618149-v", "02706816-v", "02618688-v"] # hold up
	,"come_v_up_rel": ["01627779-v", "00339738-v", "01849221-v", "01990281-v", "02625786-v", "01968569-v", "02721840-v", "01526605-v", "02213336-v", "01970348-v", "01384752-v", "01381549-v"] # come up
	,"spill_v_over_rel": ["01763101-v", "02070150-v"] # spill over
	,"tear_v_up_rel": ["01573891-v"] # tear up
	,"drive_v_up_rel": ["01850135-v"] # drive up
	,"call_v_in_rel": ["01469960-v", "00792011-v", "02487573-v", "02405120-v", "00790135-v", "02359061-v", "02312478-v"] # call in
	,"throw_v_in_rel": ["02356974-v", "01083044-v", "00914769-v"] # throw in
	,"crack_v_down_rel": ["00418921-v"] # crack down
	,"take_v_apart_rel": ["01657977-v", "01572510-v", "00643473-v"] # take apart
	,"put_v_away_rel": ["01347678-v", "02222318-v", "02494356-v", "01615991-v", "01327133-v", "01173208-v", "00778885-v"] # put away
	,"fix_v_up_rel": ["01203369-v", "01021629-v"] # fix up
	,"build_v_on_rel": ["02663643-v"] # build on
	,"fend_v_off_rel": ["02453321-v"] # fend off
	,"fall_v_in_rel": ["01989053-v", "02434859-v", "02434976-v"] # fall in
	,"wear_v_off_rel": ["00469382-v", "01254324-v"] # wear off
	,"cover_v_up_rel": ["02148369-v"] # cover up
	,"max_v_out_rel": ["02007111-v"] # max out
	,"dish_v_out_rel": ["02294436-v", "01180351-v"] # dish out
	,"hand_v_out_rel": ["02201644-v"] # hand out
	,"take_v_on_rel": ["00524682-v", "02381726-v", "02569630-v", "02236624-v", "01079480-v"] # take on
	,"scratch_v_up_rel": ["14286549-n", "13904843-n", "13385216-n", "10563610-n", "08653873-n", "07805389-n", "07392982-n", "06404147-n", "05163401-n", "04693900-n", "01250908-v", "01309143-v", "02119874-v", "02477755-v", "01549420-v", "01384752-v", "01321895-v"] # scratch
	,"strike_v_out_rel": ["00800750-v", "01509280-v", "02528833-v", "01936361-v", "01154175-v", "00346714-v"] # strike out
	,"beg_v_off_rel": ["00894221-v"] # beg off
	,"write_v_down_rel": ["01020356-v", "00315956-v"] # write down
	,"pig_v_out_rel": ["01193099-v"] # pig out
	,"drive_v_away_rel": ["02002720-v"] # drive away
	,"stick_v_out_rel": ["02713372-v", "02674564-v", "00668099-v"] # stick out
	,"speak_v_out_rel": ["01027668-v"] # speak out
	,"drag_v_in_rel": ["02677797-v"] # drag in
	,"act_v_out_rel": ["01722645-v", "01722447-v"] # act out
	,"carve_v_up_rel": ["02467662-v"] # carve up
	,"clamp_v_down_rel": ["00418921-v"] # clamp down
	,"break_v_down_rel": ["01103836-v", "00643473-v", "01784295-v", "00434374-v", "02041877-v", "01370126-v", "00209174-v", "00030647-v"] # break down
	,"turn_v_down_rel": ["02237338-v", "02502916-v", "00796976-v", "00572940-v", "00267855-v"] # turn down
	,"cross_v_out_rel": ["00800750-v"] # cross out
	,"log_v_out_rel": ["02249293-v"] # log out
	,"wipe_v_up_rel": ["01393339-v"] # wipe up
	,"shut_v_out_rel": ["02449340-v"] # shut out
	,"warm_v_up_rel": ["02444397-v", "00373112-v", "00373250-v", "00100905-v", "00027064-v"] # warm up
	,"fork_v_out_rel": ["02293321-v"] # fork out
	,"tear_v_off_rel": ["00178898-v"] # tear off
	,"button_v_up_rel": ["01041061-v"] # button up
	,"flatten_v_out_rel": ["00463469-v"] # flatten out
	,"live_v_down_rel": ["02615300-v"] # live down
	,"slow_v_down_rel": ["00439958-v", "00440580-v", "00440786-v", "00438495-v", "00026385-v"] # slow down
	,"push_v_back_rel": ["00980779-n", "01506157-v"] # push back
	,"sleep_v_in_rel": ["00015806-v", "01177314-v"] # sleep in
	,"take_v_away_rel": ["01434278-v", "00173338-v", "00179311-v", "02205719-v", "01166940-v", "00571061-v", "00532115-v"] # take away
	,"louse_v_up_rel": ["02527651-v"] # louse up
	,"scale_v_up_rel": ["00428418-v"] # scale up
	,"invite_v_out_rel": ["02486693-v"] # invite out
	,"head_v_up_rel": ["02729023-v"] # head up
	,"point_v_out-to_rel": ["01058574-v", "00924612-v", "01013230-v"] # point out
	,"square_v_up_rel": ["00145448-v", "01987648-v", "00763399-v"] # square up
	,"hold_v_out_rel": ["00027705-v", "01116585-v", "02705132-v", "02641741-v", "02618149-v"] # hold out
	,"mete_v_out_rel": ["02294436-v"] # mete out
	,"sweep_v_up_rel": ["02677797-v", "00601822-v"] # sweep up
	,"rig_v_up_rel": ["01661655-v"] # rig up
	,"call_v_up_rel": ["07169353-n", "01025455-v", "00789448-v", "00607780-v", "01097960-v"] # call up
	,"draw_v_up_rel": ["02448734-v", "01982686-v", "01863410-v", "00706804-v", "01863158-v"] # draw up
	,"pop_v_off_rel": ["02009122-v", "00358431-v"] # pop off
	,"flip_v_out_rel": ["00717921-v", "00584810-v"] # flip out
	,"suck_v_in_rel": ["01197980-v", "02765692-v", "01282142-v"] # suck in
	,"pour_v_down_rel": ["01202374-v"] # pour down
	,"buy_v_up_rel": ["02274299-v"] # buy up
	,"slacken_v_off_rel": ["00156485-v"] # slacken off
	,"slack_v_off_rel": ["00245059-v"] # slack off
	,"tie_v_in_rel": ["02736106-v", "00713167-v"] # tie in
	,"plunk_v_down_rel": ["01500572-v"] # plunk down
	,"churn_v_out_rel": ["01714095-v", "01625044-v"] # churn out
	,"pour_v_out_rel": ["00941565-v", "02070296-v", "02070150-v", "02069788-v"] # pour out
	,"smooth_v_over_rel": ["02516255-v"] # smooth over
	,"throw_v_out_rel": ["02501738-v", "02222318-v", "02401809-v", "00875806-v", "00801626-v"] # throw out
	,"switch_v_off_rel": ["01510576-v"] # switch off
	,"heat_v_up-cause_rel": ["00372665-v", "00371264-v", "00227667-v"] # heat up
	,"give_v_in_rel": ["00878348-v", "00804476-v"] # give in
	,"stay_v_over_rel": ["02652729-v"] # stay over
	,"average_v_out_rel": ["00639998-v", "02645389-v"] # average out
	,"narrow_v_down-to_rel": ["00715541-v", "00437449-v"] # narrow down
	,"let_v_down_rel": ["01973125-v", "01798936-v"] # let down
	,"fog_v_up_rel": ["02771888-v"] # fog up
	,"laugh_v_off_rel": ["00802136-v"] # laugh off
	,"wipe_v_out_rel": ["01157517-v", "00470701-v", "01621219-v", "00479391-v", "00478830-v", "00471196-v"] # wipe out
	,"siphon_v_off_rel": ["01853542-v"] # siphon off
	,"back_v_up_rel": ["02556126-v", "01997680-v", "00223109-v", "01694620-v", "01478603-v"] # back up
	,"rough_v_out_rel": ["01754452-v"] # rough out
	,"stack_v_up_rel": ["01504298-v"] # stack up
	,"hew_v_out_rel": ["01260685-v"] # hew out
	,"throw_v_away_rel": ["02222318-v", "01513430-v"] # throw away
	,"curtain_v_off_rel": ["02032010-v"] # curtain off
	,"poke_v_out_rel": ["02690093-v"] # poke out
	,"fling_v_off_rel": ["01700655-v"] # fling off
	,"clog_v_up_rel": ["01478603-v"] # clog up
	,"push_v_aside_rel": ["01873294-v", "00800930-v"] # push aside
	,"puzzle_v_out_rel": ["00634906-v"] # puzzle out
	,"ease_v_up_rel": ["01848465-v", "00156485-v", "00156276-v"] # ease up
	,"flake_v_off_rel": ["01259951-v"] # flake off
	,"mail_v_out_rel": ["01437725-v"] # mail out
	,"fit_v_in_rel": ["02700104-v"] # fit in
	,"put_v_aside_rel": ["01615991-v", "00778885-v"] # put aside
	,"gun_v_down_rel": ["01136964-v"] # gun down
	,"lay_v_down_rel": ["00665476-v"] # lay down
	,"let_v_off_rel": ["00893878-v"] # let off
	,"roll_v_over_rel": ["01867816-v", "02271667-v", "02271490-v"] # roll over
	,"dam_v_up_rel": ["01477224-v"] # dam up
	,"bubble_v_up_rel": ["01990946-v"] # bubble up
	,"nail_v_down_rel": ["02524897-v", "00715541-v", "00481941-v"] # nail down
	,"let_v_go-of_rel": ["01474550-v", "02737063-v"] # let go
	,"fill_v_in_rel": ["00833392-v", "01695567-v", "02258617-v", "01020731-v"] # fill in
	,"work_v_in_rel": ["00183506-v"] # work in
	,"dig_v_up_rel": ["01313923-v", "02143756-v"] # dig up
	,"hand_v_over_rel": ["02293321-v"] # hand over
	,"peter_v_out_rel": ["02683671-v", "00099517-v"] # peter out
	,"hunt_v_down_rel": ["01143838-v"] # hunt down
	,"simmer_v_down_rel": ["01763829-v"] # simmer down
	,"gum_v_up_rel": ["01357288-v"] # gum up
	,"dress_v_down_rel": ["00824767-v", "00045346-v"] # dress down
	,"call_v_out_rel": ["00912048-v", "00975584-v", "00868979-v"] # call out
	,"grow_v_up_rel": ["02540347-v"] # grow up
	,"hunker_v_down_rel": ["01545314-v", "02146377-v", "00819335-v"] # hunker down
	,"die_v_down_rel": ["00242026-v", "00224168-v"] # die down
	,"prop_v_up_rel": ["01219004-v"] # prop up
	,"catch_v_on_rel": ["00590366-v", "00543287-v"] # catch on
	,"hide_v_out_rel": ["02145814-v"] # hide out
	,"shut_v_down_rel": ["02426395-v"] # shut down
	,"lace_v_up_rel": ["01521603-v"] # lace up
	,"bring_v_off_rel": ["02522864-v"] # bring off
	,"seal_v_off_rel": ["01354006-v", "01126846-v"] # seal off
	,"wolf_v_down_rel": ["01169205-v"] # wolf down
	,"smash_v_up_rel": ["01566705-v"] # smash up
	,"carry_v_away_rel": ["01434278-v"] # carry away
	,"take_v_home_rel": ["02289854-v"] # take home
	,"bog_v_down_rel": ["00363742-v", "01835103-v", "01834896-v", "00363916-v"] # bog down
	,"go_v_out_rel": ["02015598-v", "01842204-v", "02011437-v", "00352419-v", "02667558-v", "02486232-v"] # go out
	,"knock_v_over_rel": ["01909978-v"] # knock over
	,"move_v_out_rel": ["02404904-v", "01856211-v"] # move out
	,"come_v_on_rel": ["00423702-v", "02053941-v", "00248659-v", "01526605-v", "00348103-v"] # come on
	,"cast_v_down_rel": ["01814396-v"] # cast down
	,"pay_v_off_rel": ["02292004-v", "02352019-v", "02256853-v", "02253456-v", "02284803-v", "01153947-v"] # pay off
	,"doll_v_up_rel": ["00043078-v"] # doll up
	,"round_v_off_rel": ["00145147-v", "00473799-v", "00145623-v"] # round off
	,"beat_v_up_rel": ["01397210-v", "01385643-v"] # beat up
	,"burn_v_out_rel": ["00435294-v"] # burn out
	,"die_v_away_rel": ["00245059-v"] # die away
	,"take_v_out_rel": ["02404904-v", "01485513-v", "00179311-v", "02239261-v", "02486693-v", "01352390-v", "02326955-v", "02311387-v", "01995211-v", "01854132-v", "01351170-v", "01166940-v", "00677021-v", "00615774-v"] # take out
	,"get_v_out_rel": ["02015598-v", "01214597-v", "02015168-v", "01009986-v", "01995211-v", "00935987-v", "00810729-v"] # get out
	,"clock_v_in_rel": ["00966330-v"] # clock in
	,"stock_v_up_rel": ["02323286-v"] # stock up
	,"crank_v_up_rel": ["01858796-v", "01595149-v"] # crank up
	,"rub_v_off_rel": ["01254013-v"] # rub off
	,"push_v_up_rel": ["01873530-v", "02713852-v"] # push up
	,"get_v_in_rel": ["02016523-v", "02585860-v", "02239405-v", "02015384-v"] # get in
	,"serve_v_up_rel": ["01180351-v"] # serve up
	,"hold_v_in_rel": ["02711114-v", "02510337-v", "02146790-v"] # hold in
	,"let_v_on_rel": ["00933821-v"] # let on
	,"dress_v_up_rel": ["00044149-v", "00293528-v", "01670315-v", "00051761-v", "00044797-v"] # dress up
	,"give_v_up_rel": ["02303331-v", "02227741-v", "01083044-v", "02680814-v", "02345647-v", "02316304-v", "02367032-v", "02235229-v", "01115585-v", "00613393-v", "02423650-v", "01196524-v"] # give up
	,"slip_v_on_rel": ["00051170-v"] # slip on
	,"crank_v_out_rel": ["01753272-v"] # crank out
	,"get_v_down_rel": ["01973486-v", "01973125-v", "01958452-v", "01201856-v", "01814396-v", "01020356-v", "00345761-v"] # get down
	,"butt_v_in_rel": ["00780191-v"] # butt in
	,"bring_v_in_rel": ["02078591-v", "02289295-v", "02247390-v", "02262932-v", "02080783-v"] # bring in
	,"laugh_v_away_rel": ["00802136-v"] # laugh away
	,"tone_v_down_rel": ["02191311-v", "00933566-v"] # tone down
	,"contract_v_out_rel": ["02410719-v", "00798402-v"] # contract out
	,"listen_v_in_rel": ["02170304-v", "02189714-v"] # listen in
	,"line_v_up_rel": ["02704213-v", "02213336-v", "02036755-v", "00464321-v", "02036650-v", "01073953-v"] # line up
	,"clean_v_up_rel": ["00275843-v", "02279315-v", "02254671-v", "00040766-v"] # clean up
	,"check_v_in_rel": ["00966152-v"] # check in
	,"send_v_out_rel": ["01437254-v"] # send out
	,"bubble_v_over_rel": ["01763101-v"] # bubble over
	,"camp_v_out_rel": ["02653996-v"] # camp out
	,"block_v_out_rel": ["00711236-v", "01477538-v", "01358737-v", "01006699-v"] # block out
	,"put_v_on_rel": ["00050652-v", "00184511-v", "01665185-v", "01649809-v", "00184786-v", "01649251-v", "01363648-v", "00854904-v", "00046151-v", "01116857-s"] # put on
	,"choke_v_off_rel": ["00391417-v", "01478603-v"] # choke off
	,"phase_v_out_rel": ["01642820-v"] # phase out
	,"bow_v_out_rel": ["02380980-v", "02380760-v"] # bow out
	,"rule_v_out_rel": ["02629390-v", "01147562-v", "00685419-v"] # rule out
	,"tip_v_over_rel": ["01909978-v", "01909397-v"] # tip over
	,"slip_v_in_rel": ["01025602-v"] # slip in
	,"spill_v_out_rel": ["02070150-v"] # spill out
	,"bring_v_together_rel": ["01295275-v", "01607072-v"] # bring together
	,"factor_v_in_rel": ["00640650-v", "00640385-v"] # factor in
	,"seek_v_out_rel": ["01317424-v"] # seek out
	,"flare_v_up_rel": ["02764245-v", "00307785-v"] # flare up
	,"set_v_about_rel": ["02439281-v", "01651293-v", "00345761-v"] # set about
	,"pull_v_through_rel": ["02619924-v", "02551832-v"] # pull through
	,"branch_v_out_rel": ["00436404-v"] # branch out
	,"lock_v_up_rel": ["01348452-v", "01347678-v"] # lock up
	,"keep_v_out_rel": ["02449340-v", "00118435-v"] # keep out
}

#print(len(MWE_ERG_WN_MAPPING))
#print(MWE_ERG_WN_MAPPING['_line_v_up_rel'])
