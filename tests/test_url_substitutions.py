import pytest
import discord
from url_substitute_bot import UrlSubstituteBot

url_replacements = {
    "www.instagram.com": "www.ddinstagram.com",
    "twitter.com": "vxtwitter.com",
    "x.com": "vxtwitter.com",
    "www.reddit.com": "www.rxyddit.com",
    "www.tiktok.com": "www.tfxktok.com"
}

url_expected_substitions = {
    "https://www.tiktok.com/@el_prell/video/7204945070431194410":
        "https://www.tfxktok.com/@el_prell/video/7204945070431194410",
    "https://www.reddit.com/r/SteamController/comments/b872h0/steam_controller_connection_guide/":
        "https://www.rxyddit.com/r/SteamController/comments/b872h0/steam_controller_connection_guide/",
    "https://www.instagram.com/reel/C6YNI8LIPFh/": "https://www.ddinstagram.com/reel/C6YNI8LIPFh/",
    "other text https://www.instagram.com/reel/C6YNI8LIPFh more text":
        "other text https://www.ddinstagram.com/reel/C6YNI8LIPFh more text",
    "https://x.com/Lord_Arse/status/1798816710482428412":
        "https://vxtwitter.com/Lord_Arse/status/1798816710482428412",
    "https://twitter.com/Lord_Arse/status/1798816710482428412":
        "https://vxtwitter.com/Lord_Arse/status/1798816710482428412",
    "http://twitter.com/Lord_Arse/status/1798816710482428412":
        "http://vxtwitter.com/Lord_Arse/status/1798816710482428412",
    "http://google.com": "http://google.com",
    "https://www.tiktok.com/test https://www.reddit.com/test":
        "https://www.tfxktok.com/test https://www.rxyddit.com/test",
    "https://cdn.discordapp.com/attachments/259688847024062464/1248592609493127238/rapidsave.com_we_had_a_good_run_fellas-np3awsm3vm3d1.mp4?ex=66cdb1fb&is=66cc607b&hm=e99bc0599ab6666c22ea0ec6b17d12f0dc4af20d57361d21bfa891a27182633b&":
        "https://cdn.discordapp.com/attachments/259688847024062464/1248592609493127238/rapidsave.com_we_had_a_good_run_fellas-np3awsm3vm3d1.mp4?ex=66cdb1fb&is=66cc607b&hm=e99bc0599ab6666c22ea0ec6b17d12f0dc4af20d57361d21bfa891a27182633b&",
    # "<https://twitter.com/Lord_Arse/status/1798816710482428412>":
        # "<https://twitter.com/Lord_Arse/status/1798816710482428412>",
}


test_bot = UrlSubstituteBot(url_replacements=url_replacements,
                            webhook_url=(
                            "https://discord.com/api/webhooks/1111111111111111111/"
                            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            ),
                            bot_token='',
                            config_path='',
                            intents=discord.Intents.default())


@pytest.mark.parametrize("sample_with_url, expected_substition",
                         url_expected_substitions.items(),
                         ids=url_expected_substitions.keys())
def test_substitions_expected(sample_with_url, expected_substition):
    actual_substitution = test_bot._url_sub(sample_with_url)
    assert actual_substitution == expected_substition