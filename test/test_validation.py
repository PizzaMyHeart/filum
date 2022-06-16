import unittest
from filum.exceptions import InvalidThreadId, InvalidUrl

from filum.validation import is_valid_id, is_valid_url


class TestInputValidation(unittest.TestCase):
    def test_is_valid_url(self):
        self.assertTrue(is_valid_url('https://www.reddit.com/r/JuniorDoctorsUK/comments/tomns3/im_a_doctor_now_working_in_the_healthtech_space/'))
        self.assertTrue(is_valid_url('https://news.ycombinator.com/item?id=31654257'))

        self.assertTrue(is_valid_url('https://stats.stackexchange.com/questions/578023/comparing-log-likelihood-of-nested-gam-models'))

        # Sites on Stack Exchange with unique domains
        self.assertTrue(is_valid_url('https://stackoverflow.com/questions/72349922/tableau-not-recognizing-snowflake-odbc-drivers-on-mac'))
        self.assertTrue(is_valid_url('https://serverfault.com/questions/357108/what-permissions-should-my-website-files-folders-have-on-a-linux-webserver'))
        self.assertTrue(is_valid_url('https://askubuntu.com/questions/17823/how-to-list-all-installed-packages'))
        self.assertTrue(is_valid_url('https://superuser.com/questions/46139/what-does-source-do'))


        with self.assertRaises(InvalidUrl):
            is_valid_url('https://www.reddit.com/r/Python/')
            is_valid_url('https://stackoverflow.blog/2022/06/06/remote-work-is-killing-big-offices-cities-must-change-to-survive/?cb=1')
            is_valid_url('https://stackoverflow.com/users/9373782/pizza')
            is_valid_url('https://news.ycombinator.com/newest')

    def test_is_valid_id(self):
        self.assertTrue(is_valid_id(1))
        
        with self.assertRaises(InvalidThreadId):
            is_valid_id(0)
            is_valid_id('1')
            is_valid_id(-1)


if __name__ == '__main__':
    unittest.main()


# flake8: noqa