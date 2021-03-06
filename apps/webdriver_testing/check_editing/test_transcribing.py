#!/usr/bin/python
# -*- coding: utf-8 -*-
from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.editor_pages import dialogs
from apps.webdriver_testing.editor_pages import unisubs_menu
from apps.webdriver_testing.editor_pages import subtitle_editor 
from apps.webdriver_testing.data_factories import UserFactory
import os
import time

class TestCaseTranscribing(WebdriverTestCase):
    """Tests for the Subtitle Transcription editor page.
        
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.video_pg = video_page.VideoPage(self)
        self.user = UserFactory.create(username = 'user')
        self.create_modal = dialogs.CreateLanguageSelection(self)
        self.sub_editor = subtitle_editor.SubtitleEditor(self)
        self.unisubs_menu = unisubs_menu.UnisubsMenu(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.video_pg.add_subtitles()
        self.create_modal.create_original_subs('English', 'English')
        self.create_modal.continue_past_help()
        self.typed_subs = self.sub_editor.type_subs()


    def test_display__normal(self):
        """Manually entered unsynced subs display in editor.

        """
        self.assertEqual(self.typed_subs, self.sub_editor.subtitles_list())


    def test_save(self):
        """Manually entered unsynced subs are saved upon save and exit.
        
        """
        curr_url = self.sub_editor.current_url()
        self.sub_editor.save_and_exit()
        self.sub_editor.open_page(curr_url)
        self.assertEqual(self.typed_subs, self.sub_editor.subtitles_list())

        

    def test_close__abruptly(self):
        """Test subs are saved when browser closes abruptly.
      
        Note: the browser needs to be open for about 80 seconds for saving.
        """
        time.sleep(90)
        self.sub_editor.open_page("")
        self.sub_editor.handle_js_alert('accept')
        time.sleep(5)
        self.video_pg.open_video_page(self.test_video.video_id)
        self.unisubs_menu.open_menu()
        self.assertEqual(self.create_modal.warning_dialog_title(), 
            'Resume editing?')
        self.create_modal.click_dialog_continue()
        self.create_modal.click_dialog_continue()
        time.sleep(5)
        self.assertEqual(self.typed_subs, self.sub_editor.subtitles_list(),
            'Existing bug: https://unisubs.sifterapp.com/issue/1552')

    def test_download(self):
        """Manually entered unsynced subs can be download from check page.

        """
        EXPECTED_UNSYNCED_TEXT = """
1
99:59:59,000 --> 99:59:59,000
I'd like to be 

2
99:59:59,000 --> 99:59:59,000
Under the sea

3
99:59:59,000 --> 99:59:59,000
In an octopus' garden in the shade.

4
99:59:59,000 --> 99:59:59,000
He'd let me in

5
99:59:59,000 --> 99:59:59,000
Knows where we've been

6
99:59:59,000 --> 99:59:59,000
In his octopus' garden in the shade.

"""        
        
        self.sub_editor.continue_to_next_step()
        #Past Sync
        self.sub_editor.continue_to_next_step()
        #Past Description
        self.sub_editor.continue_to_next_step()
        #In Check Step - download subtitles
        saved_subs = self.sub_editor.download_subtitles()
        self.assertEqual (saved_subs.strip(), EXPECTED_UNSYNCED_TEXT.strip())









