"""
Should include tests for the matcher.
"""
from typing import Optional, List
from unittest import TestCase
from spacy import load, Language
from spacy.matcher import Matcher
from merge_idioms.service import build_idiom_matcher
from merge_idioms.config import BASE_NLP_MODEL


class TestMergeIdiomsPipeline(TestCase):
    pass

    nlp: Optional[Language] = None
    idiom_matcher: Optional[Matcher] = None

    @classmethod
    def setUpClass(cls):
        """
        https://stackoverflow.com/a/12202239
        """
        # prepare resource, before running any tests below
        # I get some rsrc-related warning. Not sure why.
        nlp = load(BASE_NLP_MODEL)
        nlp.add_pipe("add_special_cases", before="tok2vec")
        # set these as the global variables.
        cls.nlp = nlp
        cls.idiom_matcher = build_idiom_matcher(nlp.vocab)

    def get_lemmas(self, sent: str) -> List[str]:
        doc = self.nlp(sent)
        matches = self.idiom_matcher(doc)
        return [
            self.idiom_matcher.vocab.strings[lemma_id]
            for (lemma_id, _, _) in matches
        ]

    # rigorously testing for hyphenated terms.
    def test_match_catch_22(self):
        sent_1 = "qualities attributed to the drug. It is a catch-22 for any trainer or owner."
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_match_catch_22_no_hyphen(self):
        sent_1 = "qualities attributed to the drug. It is a catch 22 for any trainer or owner."
        doc = self.nlp(sent_1)
        matches = self.idiom_matcher(doc)
        self.assertTrue(matches)

    def test_match_catch_22_capitalised(self):
        sent_1 = "qualities attributed to the drug. It is a Catch-22 for any trainer or owner."
        doc = self.nlp(sent_1)
        matches = self.idiom_matcher(doc)
        self.assertTrue(matches)

    def test_match_blow_by_blow(self):
        sent_1 = "He literally gives a blow-by-blow of how he killed her"
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_match_blow_by_blow_no_hyphen(self):
        sent_1 = "He literally gives a blow by blow of how he killed her"
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_match_blow_by_blow_capitalised(self):
        sent_1 = "He literally gives a Blow-By-Blow of how he killed her"
        # how should you fix this...?
        # we are doing exact match... at least for hyphenated terms.
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_balls_out(self):
        sent_1 = " in terms of rhyme, meter, and balls-out swagger. "
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_balls_out_capitalised_one(self):
        sent_1 = " in terms of rhyme, meter, and Balls-out swagger. "
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_balls_out_capitalised_two(self):
        sent_1 = " in terms of rhyme, meter, and Balls-Out swagger. "
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_balls_out_no_hyphen(self):
        sent_1 = " in terms of rhyme, meter, and balls out swagger. "
        matches = self.idiom_matcher(self.nlp(sent_1))
        self.assertTrue(matches)

    def test_come_down_to_earth(self):
        sent_1 = "Gosh, I must say perhaps we should um, sort of come down to earth" \
                 " and sample some of this delightful food."
        lemmas = self.get_lemmas(sent_1)
        self.assertIn("come down to earth", lemmas)

    def test_come_down_to_earth_capitalised(self):
        sent_1 = "Gosh, I must say perhaps we should um, sort of come down to Earth" \
                 " and sample some of this delightful food."
        lemmas = self.get_lemmas(sent_1)
        self.assertIn("come down to earth", lemmas)

    def test_article_a_optional(self):
        sent = "I hope a couple of you shed tear when you heard I'd carked it."
        lemmas = self.get_lemmas(sent)
        self.assertIn("shed a tear", lemmas)

    def test_article_an_optional(self):
        sent = "Because she would not take no for answer."
        lemmas = self.get_lemmas(sent)
        self.assertIn("take no for an answer", lemmas)

    def test_article_the_optional(self):
        sent = "You want a secure computer and online experience, " \
               "then take the bull by horns and make it happen."
        lemmas = self.get_lemmas(sent)
        self.assertIn("take the bull by the horns", lemmas)

    def test_comma_optional(self):
        sent = "Also, all those who believe that marriage makes people this that and the other" \
               " more than cohabitation is relying on OLD studies. "
        lemmas = self.get_lemmas(sent)
        self.assertIn("this, that, and the other", lemmas)

    def test_and_not_optional(self):
        sent = "... unable to conceive how a pure simple mind can exist without" \
               " any substance annexed to it."
        lemmas = self.get_lemmas(sent)
        self.assertNotIn("pure and simple", lemmas)

    def test_shoot_em_up(self):
        sent = "I think the advent of video games and third-person shoot 'em up games " \
               "did more for the zombie genre than a couple movies even."
        lemmas = self.get_lemmas(sent)
        self.assertIn("shoot 'em up", lemmas)

    def test_shoot_em_up_alts(self):
        # 1. hyphenated form.
        sent_1 = "I think the advent of video games and third-person shoot-em-up games " \
                 "did more for the zombie genre than a couple movies even."
        # 2. hyphenated with '
        sent_2 = "I think the advent of video games and third-person shoot-'em-up games " \
                 "did more for the zombie genre than a couple movies even."
        # 3. 'em -> them
        sent_3 = "I think the advent of video games and third-person shoot them up games " \
                 "did more for the zombie genre than a couple movies even."
        lemmas_1 = self.get_lemmas(sent_1)
        lemmas_2 = self.get_lemmas(sent_2)
        lemmas_3 = self.get_lemmas(sent_3)
        self.assertIn("shoot 'em up", lemmas_1)
        self.assertIn("shoot 'em up", lemmas_2)
        self.assertIn("shoot 'em up", lemmas_3)

    def test_beat_around_the_bush(self):
        sent = "Just stop beating around the bush and tell me what the problem is!"
        lemmas = self.get_lemmas(sent)
        self.assertIn("beat around the bush", lemmas)

    def test_beat_around_the_bush_alt(self):
        # around -> about
        sent = "Just stop beating about the bush and tell me what the problem is!"
        lemmas = self.get_lemmas(sent)
        self.assertIn("beat around the bush", lemmas)
        
    def test_have_blood_on_ones_hands(self):
        sent = "Try running, you'll have blood on your hands."
        lemmas = self.get_lemmas(sent)
        self.assertIn("have blood on one's hands", lemmas)

    def test_have_blood_on_ones_hands_alt(self):
        # have blood -> have one's blood
        sent = "but I think you'd prefer it than to have her blood on your hands."
        lemmas = self.get_lemmas(sent)
        self.assertIn("have blood on one's hands", lemmas)
