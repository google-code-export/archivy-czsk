'''
Created on 3.7.2012

@author: marko
'''
import re
""""account_playback_token=&ptk=youtube_none&allow_embed=1&rvs=view_count=181%2C222&author=91pontus&length_seconds=388&id=5M23P1roe3U&title=Woody+Woodpecker%3A+Woody+and+the+Beanstalk+Swedish+Movie,view_count=106%2C994&author=ErisTheFairest5&length_seconds=374&id=4tjiDrn6WPQ&title=The+Bird+Who+Came+To+Dinner,view_count=2%2C374%2C232&author=CantinhoChSite&length_seconds=419&id=d0SZuBcBx90&title=Novo+Pica+Pau+-+Montanha+De+Velocidade+Do+Dem%C3%B4nio+Montanha,view_count=128%2C343&author=woodywoodpecker1999&length_seconds=388&id=SqKOTGbCnWQ&title=Sleepwalking+Woody,view_count=299%2C250&author=hermankatnip&length_seconds=397&id=GIj8qc-lgOI&title=Woody+Woodpecker+-+Pantry+Panic+%281941%29+Restored,view_count=1%2C324%2C884&author=woodywoodpecker1999&length_seconds=390&id=VfkZqyGJ3B0&title=Woody+and+Meany,view_count=645%2C110&author=CartoonGR&length_seconds=374&id=1W46aOnBNBo&title=%CE%93%CE%BF%CF%8D%CE%BD%CF%84%CE%B9+%CE%BF+%CE%A4%CF%81%CF%85%CF%80%CE%BF%CE%BA%CE%AC%CF%81%CF%85%CE%B4%CE%BF%CF%82+-+The+Tenants%27+Racket+%28%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CE%BB%CF%89%CF%84%CE%B9%CF%83%CE%BC%CE%AD%CE%BD%CE%BF%29,view_count=25%2C948&author=arnoldzieffel&length_seconds=375&id=4GrWNl4-HcI&title=Woody+Woodpecker+in+%22Three+Little+Woodpeckers%22,view_count=1%2C153%2C372&author=CantinhoChSite&length_seconds=335&id=4M0hoOGGEVk&title=Pica+Pau+-+O+Guloso+Z%C3%A9+Jacar%C3%A9,view_count=218%2C088&author=KrazyKartoonKid&length_seconds=415&id=OxYI9D-BKPo&title=Woody+Woodpecker+-+The+Hollywood+Matador+%281942%29,view_count=2%2C100%2C463&author=lib1975&length_seconds=358&id=fFz4BYh9O2E&title=Woody+Woodpecker+-+Under+the+Counter+Spy,view_count=253%2C952&author=espermatozoideism&length_seconds=1658&id=F28zgA3l1H0&title=Pica+pau+Woody+Woodpecker+meu+desenho+predileto+gravado+pela+Tv+Record+show+de+bola&vq=auto&fexp=905603,914501,906043,910007,907217,907335,921602,919306,922600,919316,920704,924500,924700,913542,919324,920706,907344,912706,902518&allow_ratings=1&keywords=yt:crop=4:3,Woody,Woodpecker,For,The,Love,Of,Pizza,[English,Version]&track_embed=0&view_count=89855&video_verticals=[319,+3,+36]&fmt_list=43/640x360/99/0/0,34/640x360/9/0/115,18/640x360/9/0/115,5/320x240/7/0/0,36/320x240/99/0/0&author=woodywoodpecker277&muted=0&length_seconds=353&token=vjVQa1PpcFM8xXiJgjxmralFuWdyGe9JopaYXsJrKy0=&has_cc=False&tmi=1&ftoken=&status=ok&watermark=,http://s.ytimg.com/yt/img/watermark/youtube_watermark-vflHX6b6E.png,http://s.ytimg.com/yt/img/watermark/youtube_hd_watermark-vflAzLcD6.png&timestamp=1341311813&storyboard_spec=http://i1.ytimg.com/sb/l3D3AJa5q10/storyboard3_L$L/$N.jpg|48#27#100#10#10#0#default#bs2IDk11SUuEPsjzFHO8GjvbvSU|60#45#72#10#10#5000#M$M#xaYaeShIq6esi-gVx0__csmmRwU|120#90#72#5#5#5000#M$M#QPR6qtlPvQWCjPVsTivMc_I5W-E&plid=AATD6n4qsKZc_24j&endscreen_module=http://s.ytimg.com/yt/swfbin/endscreen-vflJQXhqO.swf&url_encoded_fmt_stream_map=
url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v16.lscache5.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dcp%252Cid%252Cip%252Cipbits%252Citag%252Cratebypass%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26ms%3Dau%26itag%3D43%26ip%3D91.0.0.0%26signature%3DC399DAAF4884015FB0D0A143BB7417238449740B.7EFF2E8D356EEB27B91D3C6FB6BF2094158879D4%26sver%3D3%26mt%3D1341311597%26ratebypass%3Dyes%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&
    fallback_host=tc.v16.cache5.c.youtube.com&
    type=video%2Fwebm%3B+codecs%3D%22vp8.0%2C+vorbis%22&
    itag=43,
url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v1.lscache1.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D34%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DA200880BCE5777034FC17BA0C5477A61D3D4E1BE.4D5E57E8F5F3D2758516545BEBE086FD227A44AD%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&
    fallback_host=tc.v1.cache1.c.youtube.com&
    type=video%2Fx-flv&
    itag=34,
url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v9.lscache6.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dcp%252Cid%252Cip%252Cipbits%252Citag%252Cratebypass%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26ms%3Dau%26itag%3D18%26ip%3D91.0.0.0%26signature%3DBE2BB23A6B225C2E6A849FC736EEA85E41A1D85B.378DF9E5BD9752D99FEB3316C812CA726B5A50B3%26sver%3D3%26mt%3D1341311597%26ratebypass%3Dyes%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&
    fallback_host=tc.v9.cache6.c.youtube.com&
    type=video%2Fmp4%3B+codecs%3D%22avc1.42001E%2C+mp4a.40.2%22&
    itag=18,
url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v15.lscache2.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D5%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DD7AE208F40BFF176144E4B9B0EED5E248778F5D6.9FEC6A02FAE1CFE2531A76410457739B0CFA732D%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=small&
    fallback_host=tc.v15.cache2.c.youtube.com&
    type=video%2Fx-flv&
    itag=5,
url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v18.lscache1.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D36%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DCB22FDDD863BC300EDA2AAABB8A6F9A4413EE300.7CB53A8CEA1EFA4061CD0D601612DE6130863EE9%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=small&
    fallback_host=tc.v18.cache1.c.youtube.com&
    type=video%2F3gpp%3B+codecs%3D%22mp4v.20.3%2C+mp4a.40.2%22&
    itag=36&
    
    no_get_video_log=1&avg_rating=4.59322033898&video_id=l3D3AJa5q10&sendtmp=1&pltype=content&thumbnail_url=http://i1.ytimg.com/vi/l3D3AJa5q10/default.jpg&title=Woody+Woodpecker+-+For+The+Love+Of+Pizza+[English+Version]
"""
data='account_playback_token=&ptk=youtube_none&allow_embed=1&rvs=view_count=181%2C222&author=91pontus&length_seconds=388&id=5M23P1roe3U&title=Woody+Woodpecker%3A+Woody+and+the+Beanstalk+Swedish+Movie,view_count=106%2C994&author=ErisTheFairest5&length_seconds=374&id=4tjiDrn6WPQ&title=The+Bird+Who+Came+To+Dinner,view_count=2%2C374%2C232&author=CantinhoChSite&length_seconds=419&id=d0SZuBcBx90&title=Novo+Pica+Pau+-+Montanha+De+Velocidade+Do+Dem%C3%B4nio+Montanha,view_count=128%2C343&author=woodywoodpecker1999&length_seconds=388&id=SqKOTGbCnWQ&title=Sleepwalking+Woody,view_count=299%2C250&author=hermankatnip&length_seconds=397&id=GIj8qc-lgOI&title=Woody+Woodpecker+-+Pantry+Panic+%281941%29+Restored,view_count=1%2C324%2C884&author=woodywoodpecker1999&length_seconds=390&id=VfkZqyGJ3B0&title=Woody+and+Meany,view_count=645%2C110&author=CartoonGR&length_seconds=374&id=1W46aOnBNBo&title=%CE%93%CE%BF%CF%8D%CE%BD%CF%84%CE%B9+%CE%BF+%CE%A4%CF%81%CF%85%CF%80%CE%BF%CE%BA%CE%AC%CF%81%CF%85%CE%B4%CE%BF%CF%82+-+The+Tenants%27+Racket+%28%CE%9C%CE%B5%CF%84%CE%B1%CE%B3%CE%BB%CF%89%CF%84%CE%B9%CF%83%CE%BC%CE%AD%CE%BD%CE%BF%29,view_count=25%2C948&author=arnoldzieffel&length_seconds=375&id=4GrWNl4-HcI&title=Woody+Woodpecker+in+%22Three+Little+Woodpeckers%22,view_count=1%2C153%2C372&author=CantinhoChSite&length_seconds=335&id=4M0hoOGGEVk&title=Pica+Pau+-+O+Guloso+Z%C3%A9+Jacar%C3%A9,view_count=218%2C088&author=KrazyKartoonKid&length_seconds=415&id=OxYI9D-BKPo&title=Woody+Woodpecker+-+The+Hollywood+Matador+%281942%29,view_count=2%2C100%2C463&author=lib1975&length_seconds=358&id=fFz4BYh9O2E&title=Woody+Woodpecker+-+Under+the+Counter+Spy,view_count=253%2C952&author=espermatozoideism&length_seconds=1658&id=F28zgA3l1H0&title=Pica+pau+Woody+Woodpecker+meu+desenho+predileto+gravado+pela+Tv+Record+show+de+bola&vq=auto&fexp=905603,914501,906043,910007,907217,907335,921602,919306,922600,919316,920704,924500,924700,913542,919324,920706,907344,912706,902518&allow_ratings=1&keywords=yt:crop=4:3,Woody,Woodpecker,For,The,Love,Of,Pizza,[English,Version]&track_embed=0&view_count=89855&video_verticals=[319,+3,+36]&fmt_list=43/640x360/99/0/0,34/640x360/9/0/115,18/640x360/9/0/115,5/320x240/7/0/0,36/320x240/99/0/0&author=woodywoodpecker277&muted=0&length_seconds=353&token=vjVQa1PpcFM8xXiJgjxmralFuWdyGe9JopaYXsJrKy0=&has_cc=False&tmi=1&ftoken=&status=ok&watermark=,http://s.ytimg.com/yt/img/watermark/youtube_watermark-vflHX6b6E.png,http://s.ytimg.com/yt/img/watermark/youtube_hd_watermark-vflAzLcD6.png&timestamp=1341311813&storyboard_spec=http://i1.ytimg.com/sb/l3D3AJa5q10/storyboard3_L$L/$N.jpg|48#27#100#10#10#0#default#bs2IDk11SUuEPsjzFHO8GjvbvSU|60#45#72#10#10#5000#M$M#xaYaeShIq6esi-gVx0__csmmRwU|120#90#72#5#5#5000#M$M#QPR6qtlPvQWCjPVsTivMc_I5W-E&plid=AATD6n4qsKZc_24j&endscreen_module=http://s.ytimg.com/yt/swfbin/endscreen-vflJQXhqO.swf&url_encoded_fmt_stream_map=url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v16.lscache5.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dcp%252Cid%252Cip%252Cipbits%252Citag%252Cratebypass%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26ms%3Dau%26itag%3D43%26ip%3D91.0.0.0%26signature%3DC399DAAF4884015FB0D0A143BB7417238449740B.7EFF2E8D356EEB27B91D3C6FB6BF2094158879D4%26sver%3D3%26mt%3D1341311597%26ratebypass%3Dyes%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&fallback_host=tc.v16.cache5.c.youtube.com&type=video%2Fwebm%3B+codecs%3D%22vp8.0%2C+vorbis%22&itag=43,url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v1.lscache1.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D34%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DA200880BCE5777034FC17BA0C5477A61D3D4E1BE.4D5E57E8F5F3D2758516545BEBE086FD227A44AD%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&fallback_host=tc.v1.cache1.c.youtube.com&type=video%2Fx-flv&itag=34,url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v9.lscache6.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dcp%252Cid%252Cip%252Cipbits%252Citag%252Cratebypass%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26ms%3Dau%26itag%3D18%26ip%3D91.0.0.0%26signature%3DBE2BB23A6B225C2E6A849FC736EEA85E41A1D85B.378DF9E5BD9752D99FEB3316C812CA726B5A50B3%26sver%3D3%26mt%3D1341311597%26ratebypass%3Dyes%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=medium&fallback_host=tc.v9.cache6.c.youtube.com&type=video%2Fmp4%3B+codecs%3D%22avc1.42001E%2C+mp4a.40.2%22&itag=18,url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v15.lscache2.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D5%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DD7AE208F40BFF176144E4B9B0EED5E248778F5D6.9FEC6A02FAE1CFE2531A76410457739B0CFA732D%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=small&fallback_host=tc.v15.cache2.c.youtube.com&type=video%2Fx-flv&itag=5,url=http%3A%2F%2Fo-o.preferred.energotel-bts1.v18.lscache1.c.youtube.com%2Fvideoplayback%3Fupn%3D7J7EkAuyuC4%26sparams%3Dalgorithm%252Cburst%252Ccp%252Cfactor%252Cid%252Cip%252Cipbits%252Citag%252Csource%252Cupn%252Cexpire%26fexp%3D905603%252C914501%252C906043%252C910007%252C907217%252C907335%252C921602%252C919306%252C922600%252C919316%252C920704%252C924500%252C924700%252C913542%252C919324%252C920706%252C907344%252C912706%252C902518%26mt%3D1341311597%26ms%3Dau%26algorithm%3Dthrottle-factor%26itag%3D36%26ip%3D91.0.0.0%26burst%3D40%26sver%3D3%26signature%3DCB22FDDD863BC300EDA2AAABB8A6F9A4413EE300.7CB53A8CEA1EFA4061CD0D601612DE6130863EE9%26source%3Dyoutube%26expire%3D1341334415%26key%3Dyt1%26ipbits%3D8%26factor%3D1.25%26cp%3DU0hTRlNOUl9GT0NOM19LSFZFOlBoR3BRQzZTTFNO%26id%3D9770f70096b9ab5d&quality=small&fallback_host=tc.v18.cache1.c.youtube.com&type=video%2F3gpp%3B+codecs%3D%22mp4v.20.3%2C+mp4a.40.2%22&itag=36&no_get_video_log=1&avg_rating=4.59322033898&video_id=l3D3AJa5q10&sendtmp=1&pltype=content&thumbnail_url=http://i1.ytimg.com/vi/l3D3AJa5q10/default.jpg&title=Woody+Woodpecker+-+For+The+Love+Of+Pizza+[English+Version]'
for n in re.finditer('(=|,|\|)url=(?P<url>.+?)(,|\||fallback_host).+?type=(?P<type>.+?)(,|\||itag).+?itag=(?P<q>\d+)',data):
    print n