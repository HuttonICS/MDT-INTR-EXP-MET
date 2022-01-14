
from otree.api import *
c = cu

doc = 'Introduction and risk attitude lottery game based on Holt and Laury (2002).'
class C(BaseConstants):
    NAME_IN_URL = 'risk_attitude'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PAYOFF_RED_A = 40
    PAYOFF_WHITE_A = 32
    PAYOFF_RED_B = 77
    PAYOFF_WHITE_B = 2
    INFO_SHEET_DATE = 'January 2022'
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    pass
class Player(BasePlayer):
    lottery1 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery2 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery3 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery4 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery5 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery6 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery7 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery8 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery9 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery10 = models.BooleanField(widget=widgets.RadioSelectHorizontal)
    lottery_selected = models.IntegerField()
    lottery_red = models.BooleanField()
    lottery_understanding = models.IntegerField(min=0)
    consent = models.BooleanField()
def lottery_choices(player: Player):
    return [
        [True, f'A: 🔴 = {C.PAYOFF_RED_A}, ⚪ = {C.PAYOFF_WHITE_A} points'],
        [False, f'B: 🔴 = {C.PAYOFF_RED_B}, ⚪ = {C.PAYOFF_WHITE_B} points']
    ]
def lottery1_choices(player: Player):
    return lottery_choices(player)
def lottery2_choices(player: Player):
    return lottery_choices(player)
def lottery3_choices(player: Player):
    return lottery_choices(player)
def lottery4_choices(player: Player):
    return lottery_choices(player)
def lottery5_choices(player: Player):
    return lottery_choices(player)
def lottery6_choices(player: Player):
    return lottery_choices(player)
def lottery7_choices(player: Player):
    return lottery_choices(player)
def lottery8_choices(player: Player):
    return lottery_choices(player)
def lottery9_choices(player: Player):
    return lottery_choices(player)
def lottery10_choices(player: Player):
    return lottery_choices(player)
def lottery_understanding_error_message(player: Player, value):
    if value != C.PAYOFF_WHITE_A:
        return f"Your answer is wrong. For lottery A you have a 30% probability of earning {cu(C.PAYOFF_RED_A)} (if a red ball is extracted) and a 70% probability of earning {cu(C.PAYOFF_WHITE_A)} (if a white ball is extracted). Since a white ball was extracted, you earn {cu(C.PAYOFF_WHITE_A)}"
def consent_error_message(player: Player, value):
    if not value:
        return "You must consent in order to take part, otherwise please close this tab."
class InfoSheetAndConsent(Page):
    form_model = 'player'
    form_fields = ['consent']
class WaitAfterConsent(WaitPage):
    pass
class Introduction(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        from otree.settings import POINTS_CUSTOM_NAME
        from otree.settings import REAL_WORLD_CURRENCY_CODE
        from otree.currency import RealWorldCurrency
        units = POINTS_CUSTOM_NAME if POINTS_CUSTOM_NAME else "points"
        factor = cu(1 / session.config['real_world_currency_per_point'])
        rate = f"{REAL_WORLD_CURRENCY_CODE} at a rate of {RealWorldCurrency(1)} per every {factor}"
        return {"units": units, "rate": rate}
class LotteryInstructions(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        choices = dict(lottery_choices(player))
        return {
            "lottery_payoffs": f'{choices[True]} &nbsp;&nbsp; {choices[False]}',
        }
class LotteryUnderstanding(Page):
    form_model = 'player'
    form_fields = ['lottery_understanding']
    @staticmethod
    def vars_for_template(player: Player):
        from otree.settings import POINTS_CUSTOM_NAME
        units = POINTS_CUSTOM_NAME if POINTS_CUSTOM_NAME else "points"
        choices = dict(lottery_choices(player))
        return {
            "lottery_payoffs": f'{choices[True]} &nbsp;&nbsp; {choices[False]}',
            "lottery_understanding_label": f'How many {units} would you earn?',
        }
class LotteryUnderstood(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        choices = dict(lottery_choices(player))
        return {
            "lottery_payoffs": f'{choices[True]} &nbsp;&nbsp; {choices[False]}',
        }
class LotteryDecision(Page):
    form_model = 'player'
    form_fields = ['lottery1', 'lottery2', 'lottery3', 'lottery4', 'lottery5', 'lottery6', 'lottery7', 'lottery8', 'lottery9', 'lottery10']
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        # Will now randomly pick one of the 10 lotteries,
        # randomly pick a red or white ball, and apply A/B payoffs
        import random  # TODO - import at top level if possible
        lottery_selected = random.randint(1, 10)
        # Run the lottery, red (i balls) or white (10-i balls)?
        lottery_red = random.randint(1, 10) <= lottery_selected
        # There ought to be a built in list of fields to avoid this lookup:
        lottery_choice = bool([
            player.lottery1,
            player.lottery2,
            player.lottery3,
            player.lottery4,
            player.lottery5,
            player.lottery6,
            player.lottery7,
            player.lottery8,
            player.lottery9,
            player.lottery10,
        ][lottery_selected - 1])
        if lottery_choice:
            # Apply A scores
            player.payoff = C.PAYOFF_RED_A if lottery_red else C.PAYOFF_WHITE_A
        else:
            # Apply B scores
            player.payoff = C.PAYOFF_RED_B if lottery_red else C.PAYOFF_WHITE_B
        
        # Record in the player fields for logging in the DB
        player.lottery_selected = lottery_selected
        player.lottery_red = lottery_red
        
        # Finally, record message for the final app report
        participant.risk_attitude_msg = (
            f"In the lottery game, the computer picked lottery {lottery_selected}. "
            f"In this decision, you selected lottery {'A' if lottery_choice else 'B'}, "
            f"meaning that you could earn {cu(C.PAYOFF_RED_A  if lottery_choice else C.PAYOFF_RED_B)} "
            f"with {10 * lottery_selected}% probability (red), "
            f"and {cu(C.PAYOFF_WHITE_A if lottery_choice else C.PAYOFF_WHITE_B)} "
            f"with {100 - 10 * lottery_selected}% probability (white). "
            f"The computer extracted a {'red' if lottery_red else 'white'} ball, "
            f"meaning that you earned <b>{player.payoff}</b>."
        )
page_sequence = [InfoSheetAndConsent, WaitAfterConsent, Introduction, LotteryInstructions, LotteryUnderstanding, LotteryUnderstood, LotteryDecision]