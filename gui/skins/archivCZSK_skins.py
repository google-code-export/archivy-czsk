VideoAddonsContentScreen_HD = """
            <screen position="center,80" size="900,576" title="ArchivyCZSK" flags="wfBorder" transparent="0">
              <widget backgroundColor="#9f1313" font="Regular;20" halign="center" name="key_red" position="8,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
              <widget backgroundColor="#1f771f" font="Regular;20" halign="center" name="key_green" position="231,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
              <widget backgroundColor="#a08500" font="Regular;20" halign="center" name="key_yellow" position="454,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
              <widget backgroundColor="#18188b" font="Regular;20" halign="center" name="key_blue" position="677,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
              <widget name="menu" position="12,62" scrollbarMode="showOnDemand" size="435,427" transparent="1" />
              <widget alphatest="on" name="image" position="543,124" size="256,256" zPosition="2" />
              <widget font="Regular; 25" foregroundColor="yellow" halign="left" name="title" position="472,64" size="379,40" transparent="1" />
              <widget font="Regular;20" foregroundColor="yellow" halign="left" name="author" position="487,402" size="379,25" transparent="1" />
              <widget font="Regular;20" foregroundColor="yellow" halign="left" name="version" position="487,439" size="379,25" transparent="1" />
              <widget font="Regular;20" foregroundColor="white" halign="left" name="about" position="487,475" size="379,100" transparent="1" />
              <widget font="Regular;20" foregroundColor="white" halign="left" name="tip_label" position="60,540" size="397,25" transparent="1" />
              <widget name="tip_pixmap" alphatest="on" zPosition="2" position="14,539" size="35,25" />
              <widget name="status_label" position="11,497" size="300,25" font="Regular; 16"  transparent="1" halign="left" valign="center" zPosition="2" foregroundColor="white" />
            </screen>
                    """


VideoAddonsContentScreen_SD = """
            <screen position="center,center" size="720,576" title="ArchivCZSK" >
                <widget name="key_red" position="8,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="186,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="364,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="542,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="330,485" transparent="1" scrollbarMode="showOnDemand" />
                <widget name="image" position="407,90" zPosition="2" size="256,256" alphatest="on" />
                <widget name="title" position="350,55" size="370,25" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="author" position="350,355" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="version" position="350,390" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="about" position="350,425" size="370,100" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
                <ePixmap position="0,545" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/key_info.png"  zPosition="3" transparent="1" alphatest="on" />
                <widget name="menu_text" position="45,545" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen>"""
            
VideoAddonsContentScreen = """
            <screen position="center,center" size="720,576" title="ArchivCZSK" >
                <widget name="key_red" position="8,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="186,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="364,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="542,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="330,485" transparent="1" scrollbarMode="showOnDemand" />
                <widget name="image" position="407,90" zPosition="2" size="256,256" alphatest="on" />
                <widget name="title" position="350,55" size="370,25" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="author" position="350,355" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="version" position="350,390" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="about" position="350,425" size="370,100" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
                <ePixmap position="0,545" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/key_info.png"  zPosition="3" transparent="1" alphatest="on" />
                <widget name="menu_text" position="45,545" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen>"""

        
ContentScreen_SD = """
        <screen position="center,center" size="720,576" title="ArchivCZSK" >
            <widget name="key_red" position="8,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_green" position="186,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_yellow" position="364,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_blue" position="542,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="menu" position="0,55" size="720,445" transparent="1" scrollbarMode="showOnDemand" />
            <widget name="tip_pixmap" position="0,545" size="35,25" zPosition="2" alphatest="on" />
            <widget name="tip_label" position="40,545" size="535,25" valign="center" halign="left" zPosition="2" font="Regular;18" transparent="1" foregroundColor="white" />
        </screen>
        """
        
ContentScreen_HD = """
        <screen position="center,center" size="900,575" title="ContentScreen">
          <widget backgroundColor="#9f1313" font="Regular;20" halign="center" name="key_red" position="8,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#1f771f" font="Regular;20" halign="center" name="key_green" position="231,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#a08500" font="Regular;20" halign="center" name="key_yellow" position="454,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#18188b" font="Regular;20" halign="center" name="key_blue" position="677,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget name="menu" position="12,100" scrollbarMode="showOnDemand" size="885,401" transparent="1" />
          <widget font = "Regular; 16" foregroundColor = "white" halign = "left" name = "status_label" position = "12,508" size = "535,25" transparent = "1" valign = "center" zPosition = "2" /> 
          <widget alphatest="on" name="tip_pixmap" position="9,548" size="35,25" zPosition="2" />
          <widget font="Regular;18" foregroundColor="white" halign="left" name="tip_label" position="55,548" size="493,25" transparent="1" valign="center" zPosition="2" />
          <widget source="global.CurrentTime" render="Label" position="781,530" size="85,25" font="Regular;23" halign="right" backgroundColor="black" transparent="1">
            <convert type="ClockToText">Default</convert>
          </widget>
    </screen>
             """

StreamContentScreen_HD = """
        <screen name="StreamContentScreen" position="center,90" size="900,575" title="StreamContentScreen" backgroundColor="#25080808">
  <widget backgroundColor="#9f1313" font="Regular;20" halign="center" name="key_red" position="8,520" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
  <widget backgroundColor="#1f771f" font="Regular;20" halign="center" name="key_green" position="231,520" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
  <widget backgroundColor="#a08500" font="Regular;20" halign="center" name="key_yellow" position="454,520" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
  <widget backgroundColor="#18188b" font="Regular;20" halign="center" name="key_blue" position="677,520" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
  <widget name="menu" position="13,102" scrollbarMode="showOnDemand" size="530,330" transparent="1"  />
  <widget alphatest="on" name="tip_pixmap" position="8,442" size="35,25" zPosition="2" />
  <widget font="Regular;18" foregroundColor="white" halign="left" name="tip_label" position="55,442" size="535,25" transparent="1" valign="center" zPosition="2" />
  <widget name="streaminfo_label" position="604,120" size="226,34" font="Regular; 24" backgroundColor="#25080808"/>
  <widget name="protocol_label" position="579,170" size="167,25" foregroundColor="#e5b243" font="Regular; 20" backgroundColor="#25080808"/>
  <widget name="protocol" position="771,169" size="85,25" font="Regular; 20" backgroundColor="#25080808"/>
  <widget name="playdelay_label" position="580,207" size="167,25" foregroundColor="#e5b243" font="Regular; 20" backgroundColor="#25080808" />
  <widget name="path_label" position="29,60" size="838,28" font="Regular; 24" backgroundColor="#25080808"/>
  <widget name="archive_label" position="32,6" size="835,34" halign="center" font="Regular; 34" foregroundColor="yellow1" backgroundColor="#25080808" />
  <widget name="playdelay" position="770,207" size="85,25" font="Regular; 20" backgroundColor="#25080808" />
  <widget name="rtmpbuffer" position="769,244" size="85,25" font="Regular; 20" backgroundColor="#25080808"/>
  <widget name="rtmpbuffer_label" position="580,244" size="167,25" foregroundColor="#e5b243" font="Regular; 20" backgroundColor="#25080808"/>
  <widget source="global.CurrentTime" render="Label" position="757,437" size="85,25" font="Regular;23" halign="right" backgroundColor="#25080808" transparent="1">
    <convert type="ClockToText">Default</convert>
  </widget>
  <widget name="playerbuffer_label" position="581,284" size="167,25" foregroundColor="#e5b243" font="Regular; 20" backgroundColor="#25080808" />
  <widget name="playerbuffer" position="769,284" size="85,25" font="Regular; 20" backgroundColor="#25080808" />
  <widget alphatest="on" name="livestream_pixmap" position="8,442" size="35,25" zPosition="2" backgroundColor="#25080808" />
</screen> """ 

        
ContentMenuScreen_HD = """
        <screen name="CtxMenu" position="center,center" size="500,300">
                 <widget name="menu" position="0,0" size="500,290" scrollbarMode="showOnDemand" />
        </screen>"""
        
InfoScreen_HD = """
        <screen name="InfoScreen" position="center,center" size="1100,600" title="Info">
          <widget font="Regular;22" foregroundColor="yellow" name="genre" position="435,52" size="613,30" transparent="1" />
          <widget font="Regular;22" foregroundColor="yellow" name="year" position="435,106" size="613,30" transparent="1" />
          <widget font="Regular;22" foregroundColor="yellow" name="rating" position="435,158" size="613,30" transparent="1" />
          <widget font="Regular;23" foregroundColor="white" name="plot" position="433,266" size="645,310" transparent="1" />
          <widget alphatest="on" name="img" position="8,7" size="402,570" zPosition="2" />
        </screen>
        """

InfoScreen_SD = """
            <screen position="center,center" size="720,576" title="Info" >
                <widget name="genre" position="320,50" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="year" position="320,90" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="rating" position="320,130" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="plot" position="0,310" size="720,306" font="Regular;23" transparent="1" foregroundColor="white" />
                <widget name="img" position="10,0" zPosition="2" size="300,300"  alphatest="on"/>
            </screen>"""

ContextMenuScreen = """
        <screen  position="center,center" size="500,300">
                 <widget name="menu" position="0,0" size="500,290" scrollbarMode="showOnDemand" />
        </screen>"""  
        
ChangelogScreen = """
            <screen position="center,center" size="720,576" title="Info" >
                <widget name="changelog" position="0,0" size="720,576" font="Regular;18" transparent="1" foregroundColor="white" />
            </screen>"""
            
ArchiveCZSKConfigScreen_HD = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="config" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
ArchiveCZSKConfigScreen_SD = """
            <screen position="170,120" size="381,320" >
                <widget name="key_red" position="3,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="98,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="193,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="288,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,45" size="383,1" backgroundColor="#999999" />
                <widget name="config" position="0,45" size="390,245" scrollbarMode="showOnDemand" />
            </screen>"""
            
ArchiveConfigScreen_HD = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="config" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
ArchiveConfigScreen_SD = """
            <screen position="170,120" size="381,320" >
                <widget name="key_red" position="3,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="98,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="193,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="288,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,45" size="383,1" backgroundColor="#999999" />
                <widget name="config" position="0,45" size="390,245" scrollbarMode="showOnDemand" />
            </screen>"""


ShortcutsScreen_HD = """
        <screen position="center,center" size="900,576" title="ShortcutsScreen">
          <widget backgroundColor="#9f1313" font="Regular;20" halign="center" name="key_red" position="8,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#1f771f" font="Regular;20" halign="center" name="key_green" position="231,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#a08500" font="Regular;20" halign="center" name="key_yellow" position="454,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget backgroundColor="#18188b" font="Regular;20" halign="center" name="key_blue" position="677,5" shadowColor="black" shadowOffset="-2,-2" size="215,45" valign="center" zPosition="1" />
          <widget name="menu" position="7,55" scrollbarMode="showOnDemand" size="885,445" transparent="1" />
        </screen>
        """
     
ShortcutsScreen = """
            <screen position="center,center" size="610,435" title="Shortcuts" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
                <widget name="xml" position="10,415" size="590,25" zPosition="2" valign="left" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen>"""
            
DownloadListScreen = """
            <screen position="center,center" size="610,435" title="Main Menu" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
            
DownloadsScreen = """
            <screen position="center,center" size="610,435" title="Main Menu" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""


CaptchaDialog = """
        <screen name="CaptchaDialog" position="center,center" size="1100,600" zPosition="99">
                <widget source="Title" render="Label" position=" 50,12" size="1050, 33" halign="center" font="Regular;30" backgroundColor="background" shadowColor="black" shadowOffset="-3,-3" transparent="1"/>
                <eLabel position=" 20,55" size="1080,1" backgroundColor="white"/>
                <widget name="header" position="100,90" size="900,40" font="Regular;30" transparent="1" noWrap="1" />
                <widget name="text" position="114,164" size="872,50" font="Regular;46" transparent="1" noWrap="1" halign="right" valign="center"/>
                <widget name="list" position="22,272" size="1056,225" selectionDisabled="1" transparent="1"/>
                <widget name="captcha" position="450,65" zPosition="-1" size="175,70"  alphatest="on"/>
                <eLabel position="20,555" size="1060,1" backgroundColor="white" />
        </screen>"""
        
ArchivCZSKMoviePlayer_HD = """
    <screen position="50,550" size="1180,130" title="InfoBar" backgroundColor="transparent" flags="wfNoBorder">
      
      <ePixmap position="0,0" size="1180,130" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/info_bg.png" />
      
      <ePixmap position="45,20" size="120,90" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/movie.png" alphatest="blend" />
      
      <eLabel position="180,10" size="2,110" backgroundColor="white" />
      
      <widget source="session.CurrentService" render="Label" position="202,11" size="710,30" font="Regular;28" backgroundColor="background" transparent="1">
            <convert type="ServiceName">Name</convert>
      </widget>
      
      <ePixmap position="215,58" size="677,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/prog_bg.png" zPosition="1" alphatest="on" />
      
      <widget name="buffer_slider" position="216,58" size="675,16" zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/prog_buffer.png" transparent="1" />
      
      <widget source="session.CurrentService" render="Progress" position="216,58" size="675,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/prog.png" zPosition="3" transparent="1">
        <convert type="ServicePosition">Position</convert>
      </widget>
      
      <widget source="session.CurrentService" render="PositionGauge" position="216,58" size="675,16" zPosition="4" transparent="1">
        <convert type="ServicePosition">Gauge</convert>
      </widget>
      
      <widget source="session.CurrentService" render="Label" position="215,90" size="120,28" font="Regular;23" halign="left" backgroundColor="background" shadowColor="black" shadowOffset="-2,-2" transparent="1">
        <convert type="ServicePosition">Position,ShowHours</convert>
      </widget>
      
      <widget source="session.CurrentService" render="Label" position="335,90" size="435,28" font="Regular;23" halign="center" backgroundColor="background" shadowColor="black" shadowOffset="-2,-2" transparent="1">
        <convert type="ServicePosition">Length,ShowHours</convert>
      </widget>
      
      <widget source="session.CurrentService" render="Label" position="770,90" size="120,28" font="Regular;23" halign="right" backgroundColor="background" shadowColor="black" shadowOffset="-2,-2" transparent="1">
        <convert type="ServicePosition">Remaining,Negate,ShowHours</convert>
      </widget>
      
      <eLabel position="930,10" size="2,110" backgroundColor="white" />
      
      <widget source="global.CurrentTime" render="Label" position=" 960,10" size="120,24" font="Regular;24" backgroundColor="#25080808" shadowColor="black" shadowOffset="-2,-2" transparent="1">
        <convert type="ClockToText">Format:%d.%m.%Y</convert>
      </widget>
      
      <widget source="global.CurrentTime" render="Label" position="1090,10" size=" 70,24" font="Regular;24" backgroundColor="#25080808" shadowColor="black" shadowOffset="-2,-2" transparent="1">
        <convert type="ClockToText">Default</convert>
      </widget>
      
      <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_dolby_off.png" position="975,97" size="57,20" zPosition="1" alphatest="blend" />
      <widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_dolby_on.png" position="975,97" size="57,20" zPosition="2" alphatest="blend">
        <convert type="ServiceInfo">IsMultichannel</convert>
        <convert type="ConditionalShowHide" />
      </widget>
      
      <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_format_off.png" position="1052,97" size="36,20" zPosition="1" alphatest="blend" />
      <widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_format_on.png" position="1052,97" size="36,20" zPosition="2" alphatest="blend">
        <convert type="ServiceInfo">IsWidescreen</convert>
        <convert type="ConditionalShowHide" />
      </widget>
      
      <widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_hd_off.png" position="1108,97" size="29,20" zPosition="1" alphatest="blend">
        <convert type="ServiceInfo">VideoWidth</convert>
        <convert type="ValueRange">0,720</convert>
        <convert type="ConditionalShowHide" />
      </widget>
      
      <widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/mplayer/ico_hd_on.png" position="1108,97" size="29,20" zPosition="2" alphatest="blend">
        <convert type="ServiceInfo">VideoWidth</convert>
        <convert type="ValueRange">721,1980</convert>
        <convert type="ConditionalShowHide" />
      </widget>
      
      <widget name="buffer_label" position="960,40" size="120,20" text="Buffer" font="Regular; 16" backgroundColor="background" transparent="1"/>
      
      <widget name="buffer_percent" position="1090,41" size="70,20" text="N/A" font="Regular; 16" backgroundColor="background" transparent="1" />
      
      <widget name="download_label" position="960,65" size="120,20" text="Speed" font="Regular; 16" backgroundColor="background" transparent="1"/>
      
      <widget name="download_speed" position="1090,65" size="70,20" text="N/A" font="Regular; 16" backgroundColor="background" transparent="1"/>
    </screen>
    """