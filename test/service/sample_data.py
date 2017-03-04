# Copyright 2016 edechaninfo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from test.utils import obj


sample_user_statuses = [
    {
        "id": 789035945014145025,
        "text": "Ede-chan is promising voice actor"
    },
    {
        "id": 789029558014135025,
        "text": "Recording will start soon :)",
        "extended_entities": {
            'media': [
                {
                    'id': 794502295782232064,
                    'media_url': 'http://pbs.twimg.com/media/hogehoge.jpg',
                    'type': 'photo'
                },
                {
                    'id': 794502295782232065,
                    'media_url': 'http://pbs.twimg.com/media/fugafuga.jpg',
                    'type': 'photo'
                }
            ]
        }
    },
    {
        "id": 789025958014135025,
        "text": "New anime program will be available soon"
    },
    {
        "id": 789025945014135025,
        "text": "We will invite Ede-chan for ANIME Fes!!"
    }
]

sample_list_statuses = [
    {
        "id": 789085945014145025,
        "text": "New cast announcement: Kaede Hondo!"
    },
    {
        "id": 789075958014135025,
        "text": "Blu-ray of KEIJO vol.1 is on sale!"
    },
    {
        "id": 789065945014135025,
        "text": "I went to Disney Land with my friend Ede-chan"
    },
    {
        "id": 789058945014135025,
        "text": "Ede-chan likes to behave like Maria-chan"
    }
]

sample_blog_data = {
    'bozo_exception': {
        'message': 'document declared as us-ascii, but parsed as utf-8'
    },
    'version': 'rss10',
    'encoding': 'utf-8',
    'entries': [
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12211554968.html',
            title='Minyami: Wake up, girls',
            link='http://ameblo.jp/fruits-box-blog/entry-12211554968.html'),
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12210698546.html',
            title='Ede: Yoru-night!',
            link='http://ameblo.jp/fruits-box-blog/entry-12210698546.html'),
        obj(id='http://ameblo.jp/fruits-box-blog/entry-12208663602.html',
            title='Ede: Pop in Q',
            link='http://ameblo.jp/fruits-box-blog/entry-12208663602.html')
    ]
}

sample_blog_data2 = {
    'bozo_exception': {
        'message': 'document declared as us-ascii, but parsed as utf-8'
    },
    'version': 'rss10',
    'encoding': 'utf-8',
    'entries': [
        obj(id='http://ameblo.jp/otakublo/entry-12311554968.html',
            title='Hondo-san has come as our guest',
            link='http://ameblo.jp/otakublo/entry-12311554968.html'),
        obj(id='http://ameblo.jp/otakublo/entry-12290698546.html',
            title="We will invite secret guest for today's program'",
            link='http://ameblo.jp/otakublo/entry-12290698546.html'),
        obj(id='http://ameblo.jp/otakublo/entry-12258663602.html',
            title='Next program will feature girlish number',
            link='http://ameblo.jp/otakublo/entry-12258663602.html')
    ]
}

sample_blog_data3 = {
    'bozo_exception': {
        'message': 'document declared as us-ascii, but parsed as utf-8'
    },
    'version': 'rss20',
    'encoding': 'utf-8',
    'entries': [
        obj(title='In these days...',
            link='http://ameblo.jp/ari-step/entry-12233144905.html'),
        obj(title='Look this',
            link='http://ameblo.jp/ari-step/entry-12226218315.html'),
        obj(title='4DX!!',
            link='http://ameblo.jp/ari-step/entry-12224195011.html')
    ]
}

sample_ameblo_blog_body = '''
<!doctype html>
<html lang="ja" class="columnB fixed" xmlns:og="http://ogp.me/ns#">
<head>
<!--base_skin_code:new,skin_code:wu_womanblog_50,default_custom_code:w_gg_usr-->
<meta charset="UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta property="fb:app_id" content="311629842256842" />
<meta property="og:locale" content="ja_JP" />
<meta property="og:title" content="Look at this :)" />
<meta property="og:type" content="article" />
<meta property="og:url" content="http://ameblo.jp/ari-step/entry-12226218315.html" />
<meta property="og:image" content="http://stat.ameba.jp/user_images/20161206/16/ari-step/46/1c/j/o0800045013815202951.jpg" />
<meta property="og:site_name" content="Step on the blue sky" />
<meta property="og:description" content="BBK BRNK with Hondo-chan and Maria-chan" />
<meta property="al:ios:url" content="jpameblo://ameblo/ari-step/entry/12226218315">
<meta property="al:ios:app_store_id" content="349442137">
<meta property="al:ios:app_name" content="Ameba">
<meta property="al:android:url" content="jpameblo://ameblo/ari-step/entry/12226218315">
<meta property="al:android:package" content="jp.ameba">
<meta property="al:android:app_name" content="Ameba">
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:url" content="http://ameblo.jp/ari-step/entry-12226218315.html" />
<meta name="twitter:title" content="Look at this :)" />
<meta name="twitter:description" content="BBK BRNK with Hondo-chan and Maria-chan" />
<meta name="twitter:image" content="http://stat.ameba.jp/user_images/20161206/16/ari-step/46/1c/j/o0800045013815202951.jpg" />
<meta name="twitter:app:country" content="JP">
<meta name="twitter:app:name:iphone" content="Ameba">
<meta name="twitter:app:id:iphone" content="349442137">
<meta name="twitter:app:url:iphone" content="jpameblo://ameblo/ari-step/entry/12226218315">
<meta name="twitter:app:name:googleplay" content="Ameba">
<meta name="twitter:app:id:googleplay" content="jp.ameba">
<meta name="twitter:app:url:googleplay" content="jpameblo://ameblo/ari-step/entry/12226218315">
<meta name="keywords" content="Look at this :),Step on the blue sky,Ari Ozawa,blog,ameba" />
<link rel="alternate" href="android-app://jp.ameba/http/ameblo.jp/ari-step/entry0-12226218315.html" />
<link rel="alternate" href="ios-app://349442137/jpameblo/ameblo.jp/ari-step/entry0-12226218315.html" />
<link rel="alternate" type="text/html" media="handheld" href="http://m.ameba.jp/m/blogArticle.do?guid=ON&unm=ari-step&articleId=12226218315" />
<link rel="alternate" type="text/html" media="only screen and(max-device-width: 640px)" href="http://s.ameblo.jp/ari-step/entry-12226218315.html" />
<link rel="canonical" href="http://ameblo.jp/ari-step/entry-12226218315.html">
<title>Look at this :) | Step on the blue sky</title>
<link rel="alternate" type="application/rss+xml" title="RSS" href="http://rssblog.ameba.jp/ari-step/rss20.xml" />
<link rel="shortcut icon" href="http://stat100.ameba.jp/common_style/img/favicon.ico" />
<link rel="apple-touch-icon-precomposed" href="http://stat100.ameba.jp/common_style/img/sp/apple-touch-icon.png" />
<link rel="stylesheet" media="screen,print" type="text/css" href="http://stat100.ameba.jp/ameblo/pc/css/amebabar/ameblo.common.hf.white-1.1.0.css" />
<link rel="stylesheet" media="screen,print" type="text/css" href="http://stat100.ameba.jp/ameblo/pc/css/amebabar/amebabar-1.3.0.css" />
<link rel="stylesheet" type="text/css" href="http://stat100.ameba.jp/ameblo/pc/css/newBlog-1.30.0.css" />
<link rel="stylesheet" type="text/css" href="http://stat100.ameba.jp/p_skin/wu_womanblog_50/css/skin.css" />
<link rel="stylesheet" media="screen,print" type="text/css" href="http://stat100.ameba.jp/ameblo/pc/css/entryDetailEventJack-1.1.0.css">
<link rel="stylesheet" media="screen,print" href="http://stat100.ameba.jp/ameblo/pc/css/freshSp-1.0.0.css" charset="UTF-8" />
<link rel="stylesheet" media="screen,print" href="http://stat100.ameba.jp/ameblo/pc/css/freshTopics-1.3.0.css" charset="UTF-8" />
<link rel="stylesheet" media="screen,print" href="http://stat100.ameba.jp/ameblo/pc/css/freshCm-1.0.0.css" charset="UTF-8" />
<link rel="stylesheet" media="screen,print" type="text/css" href="http://stat100.ameba.jp/ameblo/pc/css/bigfooter-1.13.0.css" charset="UTF-8" />
<!--[if lt IE 9]><script src="http://stat100.ameba.jp/common_style/js/library/html5js/html5.js"></script><![endif]-->
<script src="http://stat100.ameba.jp/blog/new/js/cmn/blog_head.js" charset="UTF-8"></script>
<script src="http://stat100.ameba.jp/common_style/js/library/swfobject.js" charset="UTF-8"></script>
<script src="http://stat100.ameba.jp/ad/dfp/js/dfp.js?20160912"></script>
<script type="text/javascript">
Amb.dfp.setTargetingParam('genre', 'radioactor');
Amb.dfp.setTargetingParam('adxOk', 'true');
Amb.dfp.setTargetingParam('skinCode', 'wu_womanblog_50');
Amb.dfp.setOpenX();
</script>
</head>
<body>


<script>
dataLayer = [{
  skin: 'new',
  userType: 'general',
  columnType: '2columns',
  commonPage_pageId: 'article_blog-entry'
}];
</script>
<noscript><iframe src="//www.googletagmanager.com/ns.html?id=GTM-WHNR29"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WHNR29');</script>

<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function()
{n.callMethod? n.callMethod.apply(n,arguments):n.queue.push(arguments)}
;if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1600985630194213');
fbq('track', "PageView");</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1600985630194213&ev=PageView&noscript=1"
/></noscript>
<!-- End Facebook Pixel Code -->


  <div id="fb-root"></div>
  <script>
    window.fbAsyncInit = function(){
      FB.init({
          appId  : '311629842256842',
          version: 'v2.3',
          status : true,
          xfbml  : true
      });
      FB.Event.subscribe('edge.create', function(url, html) {
        var pagePath = html.getAttribute('data-page-path') || location.href;
        dataLayer.push({ 'event':'FBevent','socialNetwork':'Facebook','socialAction':'Like','socialTarget':url,'socialPagePath':pagePath});
      });
    };
    (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/ja_JP/sdk.js#xfbml=1&version=v2.3&appId=311629842256842";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
  </script>
<script>
  window.twttr = (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0],
      t = window.twttr || {};
    if (d.getElementById(id)) return t;
    js = d.createElement(s);
    js.id = id;
    js.src = "https://platform.twitter.com/widgets.js";
    fjs.parentNode.insertBefore(js, fjs);
    t._e = [];
    t.ready = function(f) {
      t._e.push(f);
    };
    return t;
  }(document, "script", "twitter-wjs"));
  (function() {
    twttr.ready(
      function (twttr) {
        twttr.events.bind('follow', function(intentEvent) {
          var pagePath = intentEvent.target.parentNode.getAttribute('data-page-path-twitter');
          if (!pagePath) return;
          var account = intentEvent.target.getAttribute('data-screen-name');
          dataLayer.push({ 'event':'twttrevent','socialNetwork':'twitter','socialAction':'follow','socialTarget':account,'socialPagePath': pagePath});
        });
      }
    );
  })();
</script>

<!--bodyTop-->

<a name="pageTop"></a>
<div class="skinBody">
<div class="skinBody2">
<div class="skinBody3">

<ul id="keyJumpNav">
<li><a class="skinBlock" href="#blogContent">Jump to Body</a></li>
</ul>
<div id="ambHeader">
<div id="ambHeaderLeft"></div>
<div id="ambHeaderRight">
<div id="ameblo-option" class="-ameblo-cmnhf-service"></div>
<div class="-ameblo-cmnhf-register"><a class="-ameblo-cmnhf-registerBtn" href="https://user.ameba.jp/regist/registerIntro.do">New user</a></div>
</div>
</div>

<!--frameBefore-->

<div class="skinFrame">

<!--skinFrame2Upper-->

<div class="skinFrame2">

<!--subFrameTop-->

<div class="skinHeaderFrame">

<header>
<div class="skinHeaderArea">
<div class="skinHeaderArea2">

<!--headerTop-->

<div class="skinBlogHeadingGroupArea">
<hgroup>
<h1 class="skinTitleArea"><a href="http://ameblo.jp/ari-step/" class="skinTitle">Step on the blue sky</a></h1>
<h2 class="skinDescriptionArea"><span class="skinDescription">Blog by Ari Ozawa</span></h2>
</hgroup>
</div>

<!--headerBottom-->

</div>
</div>
</header>

</div>

<!--wrapBefore-->

<div class="skinContentsFrame">

<div class="skinContentsArea">
<div class="skinContentsArea2">

<!--firstContentsAreaTop-->

<div class="layoutContentsA">

<div id="main" class="skinMainArea">
<div class="skinMainArea2">

<!--subMainTop-->

<div class="globalLinkArea">
  <ul class="globalLinkAreaInner">
    <li class="globalLinkNavItem globalLinkNavTop"><a class="skinImgBtnS blogTopBtn" href="http://ameblo.jp/ari-step/"><span>Blog Top</span></a></li>
    <li class="globalLinkNavItem globalLinkNavArticle"><a class="skinImgBtnS articleListBtn" href="http://ameblo.jp/ari-step/entrylist.html"><span>Article List</span></a></li>
    <li class="globalLinkNavItem globalLinkNavImgList"><a class="skinImgBtnS imageListBtn" href="http://ameblo.jp/ari-step/imagelist.html"><span>Image List</span></a></li>
  </ul>
</div>

<div class="pagingArea detailPaging largePagingArea">
<a class="skinSimpleBtn pagingNext" href="http://ameblo.jp/ari-step/entry-12224195011.html">4DX!!<span class="pagingArrow">&nbsp;&raquo;</span></a>
</div>
<!--TopPagingBottom-->

<a name="blogContent"></a>

<article class="js-entryWrapper" data-unique-entry-id="12226218315" data-unique-entry-title="Look at this :)" data-unique-ameba-id="ari-step">
<div class="skinArticle themeNumber10069459358">
<div class="skinArticle2">
<div class="skinArticle3">

<div class="skinArticleHeader">
<div class="skinArticleHeader2">

<h1><a href="http://ameblo.jp/ari-step/entry-12226218315.html" class="skinArticleTitle" rel="bookmark">
  Look at this :)
</a>
</h1>

</div>
</div>

<div class="skinArticleBody">
<div class="skinArticleBody2">

<div class="articleDetailArea skinWeakColor">
<span class="articleTime"><time datetime="2016-12-06" pubdate="pubdate">Dec 6, 2016</time></span>
<br />
<span class="articleTheme">Theme<a href="http://ameblo.jp/ari-step/theme-10069459358.html" rel="tag">Blog</a></span>

</div>

<div class="articleText">
In the recording of BBK BRNK, <br>this is Hondo-chan and Maria-chan.<br>
<div align="left"><a id="i13815202951" class="detailOn" href="http://ameblo.jp/ari-step/image-12226218315-13815202951.html">
<img src="http://stat.ameba.jp/user_images/20161206/16/ari-step/46/1c/j/o0800045013815202951.jpg?caw=800" width="310" /></a></div><br>
Maria got a piece of bread from Hondo-chan.<br><div align="left"><a id="i13815202959" class="detailOn" href="http://ameblo.jp/ari-step/image-12226218315-13815202959.html">
<img src="http://stat.ameba.jp/user_images/20161206/16/ari-step/ab/e7/j/o0525080013815202959.jpg?caw=800" width="309" height="470" /></a></div><br>
Both two of them come with the same appearance.<br>From their back appearance, staff in the booth could not find which is who.<br><br>
BBK BRNK the giant of galaxy<br><br>is coming to climax!<br>Thank you for watching it!<br><br><br>*ari*

</div>

<!--entryBottom-->

<div class="js-hashtag hashtag-module-wrapper" data-hash-entryId="12226218315"></div>

<div class="subAdBannerHeader"><span>AD</span></div>
<div style="margin-bottom: 30px;text-align: center;">
<script type="text/javascript" src="//pagead2.googlesyndication.com/pagead/show_ads.js"></script>
</div>

<div class="articleBtnArea">
<div class="articleBtnSubArea js-popup-reblog-trigger">
</div>
</div>

<div class="articleLinkArea skinWeakColor">
</div>

<div class="skinArticleFooter">

<!-- SNSAccount -->
<div class="snsReaderModule bd skin-bd-color skinBorderColor skin-borderQuiet">
  <div class="snsReaderModuleBlog snsReaderModuleBlog--new">
    <div class="snsReaderModuleBlog__profileImg snsReaderModuleBlog__profileImg--new">
      <span class="snsReaderModuleBlogProfileImgWrap">
        <img src="http://stat.profile.ameba.jp/profile_images/20150824/22/a7/pq/j/o048007201440424701392.jpg?cpd=60" width="60" />
      </span>

    </div>
    <div class="snsReaderModuleBlog__text snsReaderModuleBlog__text--new">
      <p class="snsReaderModuleBlogNickname snsReaderModuleBlogNickname--new skinTextColor">Become Reader</p>
      <p class="snsReaderModuleBlogCopy snsReaderModuleBlogCopy--new skin-textQuiet skinWeakColor">Get Notification</p>
    </div>
    <div class="snsReaderModuleBlog__button snsReaderModuleBlog__button--new">
      <a href="http://blog.ameba.jp/reader.do?bnm=ari-step" class="snsReaderModuleBlogRegistrationButton">Become Reader<i></i></a>
    </div>
  </div>

</div>

</div>

<div class="pagingArea entryPaging">
<a class="pagingList" href="http://ameblo.jp/ari-step/entrylist.html">Article List</a>
&nbsp; | &nbsp;<a class="pagingNext" href="http://ameblo.jp/ari-step/entry-12224195011.html">4DX!!&nbsp;&raquo;</a>
</div>

<div class="articleImageListArea">
<span class="articleImageHeading">Latest Articles with Images</span>
<span class="articleImageListLink">&nbsp;<a href="http://ameblo.jp/ari-step/imagelist.html">More &gt;&gt;</a></span>
<ul>
<li>
<a href="http://ameblo.jp/ari-step/entry-12224195011.html?frm_src=thumb_module">
<img src="http://stat.ameba.jp/user_images/20161130/01/ari-step/4a/91/j/t02200124_0960054013809998471.jpg?cpd=110" width="110" height="110"  alt="4DX!!" class="articleImage" />
<span class="articleImageTitle">4DX!!</span>
</a>
<span class="articleImageDate skinWeakColor">2016-11-30</span>
</li>
</ul>
</div>

</div>
</div>

</div>
</div>
</div>
</article>

<!--PagingUpper-->
  <span id="js-snews-trigger"></span>

<!--bottomPagingTop-->

<div class="pagingArea detailPaging largePagingArea">
<a class="skinSimpleBtn pagingNext" href="http://ameblo.jp/ari-step/entry-12224195011.html">4DX!!<span class="pagingArrow">&nbsp;&raquo;</span></a>
</div>

<div style="height:130px;text-align: center;">
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<ins class="adsbygoogle"
     style="display:inline-block;width:378px;height:130px"
     data-ad-client="ca-pub-9369398376690864"
     data-ad-slot="3608104620"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
</div>

<div class="globalLinkArea">
  <ul class="globalLinkAreaInner">
    <li class="globalLinkNavItem globalLinkNavTop"><a class="skinImgBtnS blogTopBtn" href="http://ameblo.jp/ari-step/"><span>Blog Top</span></a></li>
    <li class="globalLinkNavItem globalLinkNavArticle"><a class="skinImgBtnS articleListBtn" href="http://ameblo.jp/ari-step/entrylist.html"><span>Article List</span></a></li>
    <li class="globalLinkNavItem globalLinkNavImgList"><a class="skinImgBtnS imageListBtn" href="http://ameblo.jp/ari-step/imagelist.html"><span>Image List</span></a></li>
  </ul>
</div>

<div class="category-alliance-wrapper">
  <div class="category-alliance-inner">

    <div class="category-alliance-image-ad">
      <p class="category-alliance-image-ad-text">AD</p>
      <script type="text/javascript" language="JavaScript">
      yads_ad_ds = '10206_39361';
      </script>
      <script type="text/javascript" language="JavaScript" src="http://yads.c.yimg.jp/js/yads.js"></script>
    </div>

  </div>
</div>


<div id="footer_ad">
<ul>
<li>
<div class="adcross_loader pid_191 container_div"></div>
</li>
</ul>
</div>

</div>
</div><aside>
<div class="skinSubA skinSubArea">
<div class="skinSubA2">

<!--subATop-->
<style type="text/css">
.ggNews,
.membersNews{
margin:0 auto 10px auto;
}
.ggNews h3,
.ggNews h3 a{
height:50px;
margin:0;
padding:0;
}
.membersNews h3,
.membersNews h3 a{
height:65px;
margin:0;
padding:0;
}
.ggNews .ggNewsInner,
.membersNews .ggNewsInner{
padding:10px;
background-color:#FFF;
border:10px solid #F7F7F7;
}
.ggNews .ggNewsInner div,
.membersNews .ggNewsInner div{
background-color:#FFF;
}
.ggNewsInner a{
display:block;
padding-left:6px;
margin-bottom:4px;
background:url(http://stat100.ameba.jp/common_style/img/common/icon_list.png) no-repeat 0 -1496px transparent;
}
</style>
<div class="ggNews">
<h3><a href="http://gg.ameba.jp/" target="_blank" title="AmebaGG NEWS"><img src="http://stat100.ameba.jp/p_skin/gg/img/news_gg.gif" alt="AmebaGG NEWS" /></a></h3>
<div class="ggNewsInner">
<div class="adcross_loader pid_29 container_div"></div>
</div>
</div><!--//ggNews-->
<!--GG banner-->
<div class="adcross_loader pid_20 container_div"></div>

<div class="designSelectBtnArea"><a class="designSelectBtn skinImgBtnM" target="_blank" href="http://blog.ameba.jp/reader.do?bnm=ari-step"><span>Become Reader</span></a></div>

<div class="skinMenu profileMenu">
<div class="skinMenu2">

<div class="skinMenuHeader">
<span class="skinMenuTitle">Profile</span>
</div>

<div class="skinMenuBody">


<div class="skinMenuBody2">

<div class="userProfileImageArea">
<div class="userProfileImage"><a href="http://profile.ameba.jp/ari-step/"><img width="60" height="90" alt="" src="http://stat.profile.ameba.jp/profile_images/20150824/22/a7/pq/j/o048007201440424701392.jpg" style="padding-top:0px" /></a></div>
</div>



<div class="profileUserNicknameArea">
<div class="profileUserNickname">
<em><a href="http://profile.ameba.jp/ari-step/">Ari Ozawa</a></em>
</div>
<div class="profileUserPages skinWeakColor">
<a href="http://profile.ameba.jp/ari-step/">Profile</a> | <a target="_blank" href="http://r.ca-mpr.jp/s/10/?i4a=370834&targetAmebaId=ari-step">Pigg room</a>
</div>
<div class="profileUserPages skinWeakColor">
<a href="http://now.ameba.jp/ari-step/">now</a> | 
<a href="http://group.ameba.jp/user/groups/ari-step/">guruppo</a>

</div>
</div>


<div class="profileDetailArea">
<ul>
<li>Birthday: Aug 18</li>
<li class="freeText">
Ari Ozawa
<a class="freeTextLink" href="http://profile.ameba.jp/ari-step/">Go to Next</a>
</li>
</ul>
</div>

</div>
</div>

</div>
</div>			<!--adSidePremium-->
<div class="subAdBannerArea subModule">
<div class="subAdBannerHeader"><span>AD</span></div>
<!-- Google DFP PremiumPanel -->
<div class="gpt-frame" id="div-gpt-ad-1341245475293-0" name="/7765/PremiumPanel_AmebaBlog_GG"><script>Amb.dfp.setFrameHere();</script></div>
</div>

<div class="skinMenu recentEntriesMenu">
<div class="skinMenu2">

<div class="skinMenuHeader">
<span class="skinMenuTitle">Latest Article</span>
</div>

<div class="skinMenuBody">

<ul class="skinSubList">
<li><a href="http://ameblo.jp/ari-step/entry-12226218315.html">Look at this :)</a></li>
<li><a href="http://ameblo.jp/ari-step/entry-12224195011.html">4DX!!</a></li>
</ul>

<div class="listLink">
<a href="http://ameblo.jp/ari-step/entrylist.html" >List All</a>
<p class="list"><span class="listImagetop"></span><a href="http://ameblo.jp/ari-step/imagelist.html" >Image List</a></p>
</div>

</div>

</div>
</div><div class="skinMenu calendarMenu">
<div class="skinMenu2">

<div class="skinMenuHeader">
<span class="skinMenuTitle">Calender</span>
</div>

<div class="skinMenuBody">

<div class="calendar">
<table>
<caption>
<a href="http://ameblo.jp/ari-step/archive-201611.html" class="pre">&lt;&lt;</a>December<a href="http://ameblo.jp/ari-step/archive-201701.html" class="next">&gt;&gt;</a></caption>
<tr id="weekID">
<th class="sun">Sun</th>
<th class="mon">Mon</th>
<th class="tue">Tue</th>
<th class="wed">Wed</th>
<th class="thu">Thu</th>
<th class="fri">Fri</th>
<th class="sat">Sat</th>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td>1</td>
<td>2</td>
<td>3</td>
</tr>
<tr>
<td>4</td>
<td>5</td>
<td><a href="http://ameblo.jp/ari-step/day-20161206.html">6</a></td>
<td>7</td>
<td>8</td>
<td>9</td>
<td>10</td>
</tr>
<tr>
<td>11</td>
<td>12</td>
<td>13</td>
<td>14</td>
<td>15</td>
<td>16</td>
<td>17</td>
</tr>
<tr>
<td>18</td>
<td>19</td>
<td>20</td>
<td>21</td>
<td>22</td>
<td>23</td>
<td>24</td>
</tr>
<tr>
<td>25</td>
<td>26</td>
<td>27</td>
<td>28</td>
<td>29</td>
<td>30</td>
<td>31</td>
</tr>
</table>


</div>

</div>

</div>
</div><div class="skinMenu archiveMenu">
<div class="skinMenu2">

<div class="skinMenuHeader">
<span class="skinMenuTitle">Per month</span>
</div>

<div class="skinMenuBody">

<ul class="skinSubList">
<li><a href="http://ameblo.jp/ari-step/archive1-201612.html">Dec 2016 ( 1 )</a></li>
<li><a href="http://ameblo.jp/ari-step/archive1-201611.html">Nov 2016 ( 10 )</a></li>
</ul>

<div class="listLink">
<a href="http://ameblo.jp/ari-step/archiveentrylist-201612.html" >Show List</a>
</div>

</div>

</div>
</div><div class="blogSearchForm subModule">

<form id="blogSearchForm" class="blogSearchForm" name="blogSearchForm" action="http://search.ameba.jp/search.html" method="get">
<span id="blogSearchBtn" class="blogSearchBtn">Search</span>
<input id="blogSearchInput" class="blogSearchInput" type="text" size="20" maxlength="255" name="q" title="Search in this blog" value="Search in this blog" />
<input type="hidden" name="aid" value="ari-step" />
</form>

</div>
<div class="registArea subModule">

<div class="registBtnArea">
<a class="registBtn skinImgBtnM" href="https://user.ameba.jp/regist/registerIntro.do?frmid=1012"><span>Ameba Register</span></a>
</div>

<div class="subAdList skinFieldBlock">
<div class="adcross_loader pid_190 container_div"></div>
</div>
</div><div class="rss skinFieldBlock">

<div>
<a class="rssBtn" href="http://rssblog.ameba.jp/ari-step/rss20.xml">RSS</a>
</div>

<div class="rssDescription">
<a href="http://helps.ameba.jp/trouble/copyright.html" target="_blank">*About Copyright</a>
</div>

</div>
<!--subABottom-->
<div class="subAdBannerHeader"><span>AD</span></div>

<div class="gpt-frame" id="div-gpt-ad-1341245517290-1" name="/7765/BTFSidePanel">
<script>Amb.dfp.setFrameHere();</script>
</div>


</div>
</div>
</aside>

</div>


<div class="layoutContentsB">

<aside>
<div class="skinSubB skinSubArea">
<div class="skinSubB2">

<!--subBTop-->


<!--subBBottom-->

</div>
</div>
</aside>

</div>

</div>
</div>

</div>

<!--subFrameBottom-->

</div>
</div>

<!--frameAfter-->

</div>
</div>
</div><ul class="footerNav">
<li><a class="footerNavNext" href="http://ameblo.jp/ari-step/entry-12224195011.html"><div class="footPt23">Next</div></a></li>
<li class="inactive"><span class="footerNavPrev"><div class="footPt23">Prev</div></span></li>
<li><a class="footerNavlist" href="http://ameblo.jp/ari-step/entrylist.html"><div class="footPt15">Article List</div></a></li>
<li><a id="footerNavTop" class="footerNavTop" href="#"><div class="footPt23">Go to Top</div></a></li>
</ul>
<!--bodyBottom-->

<div class="bfl-bigfooter" id="js-bigfooter" data-state="general">


  <div class="bfl-topics__outer" id="js-bigfooter-topics">
    <div class="bfl-topics bfu-clear">
      <div class="bfl-topics__headline">
        <p class="bfl-topics__headline__title bfc-headline bfc-headline--large">Ameba Favorite Blog</p>
      </div>
      <div class="bfl-news__outer bfu-clear bfu-is-hidden" id="js-bigfooter-news-outer">
        <div class="bfl-news">
          <div class="bfl-news__headline">
            <h2 class="bfl-news__headline__title bfc-headline bfc-headline--middle">Topics</h2>
            <div class="bfl-news__headline__update bfc-text--weak" id="js-new-update"></div>
          </div>
          <div class="bfl-news__content bfu-clear" id="js-bigfooter-news">
            <div class="bfl-news__text">
              <ul class="bfp-news_list bfu-clear" id="js-bigfooter-news-text"></ul>
            </div>
            <div class="bfl-news__img">
              <ul class="bfp-news_imgList" id="js-bigfooter-news-img"></ul>
            </div>
          </div>
          <div class="bfl-topics__more bfl-topics__more--full bfu-clear" id="js-bigfooter-news-more">
            <a class="bfc-more-link" href="http://ametopi.jp" data-ga-category="ametopi-more" data-ga-label="gen"><span class="bfc-more-link___text">Read more</span><i class="bfc-icon bfc-icon--more"></i></a>
          </div>
        </div>
      </div>

        <div class="bfl-ranking__outer bfu-clear bfu-is-hidden" id="js-bigfooter-ranking-outer">
          <div class="bfl-ranking__headline">
            <h2 class="bfl-ranking__headline__title bfc-headline bfc-headline--middle">Ranking</h2>
            <ul class="bfl-ranking__headline__tab bfp-ranking__tab bfu-clear" id="js-bigfooter-ranking-tab">
              <li class="bfp-ranking__tab__item" data-rank-index="0" data-ga-category="blogRankingTab-general" data-ga-label="gen">Total</li>
              <li class="bfp-ranking__tab__item" data-rank-index="1" data-ga-category="blogRankingTab-new" data-ga-label="gen">New</li>
              <li class="bfp-ranking__tab__item" data-rank-index="2" data-ga-category="blogRankingTab-trend" data-ga-label="gen">Spike</li>
              <li class="bfp-ranking__tab__item" data-rank-index="3" data-ga-category="blogRankingTab-trend-genre" data-ga-label="gen">Trend</li>
            </ul>
            <div class="bfl-ranking__headline__update bfc-text--weak" id="js-bigfooter-ranking-update"></div>
          </div>
          <div class="bfp-ranking__list__outer" id="js-bigfooter-ranking-list"></div>
          <div class="bfl-topics__more bfl-topics__more--full bfu-clear">
            <a href="" class="bfc-more-link" id="js-bigfooter-ranking-more" data-ga-category="blogRanking-more" data-ga-label="gen"><span class="bfc-more-link___text">Read more</span><i class="bfc-icon bfc-icon--more"></i></a>
          </div>
        </div>
        <div class="bfl-topics__button">
          <div class="bfc-button--large"><a href="http://official.ameba.jp/" class="bfc-button__link bfu-valign-m" data-ga-category="button-officialTop" data-ga-label="gen"><span class="bfc-button__text">Top</span></a></div>
        </div>
    </div>
  </div>

<div id="js-freshTopics"></div>
<div id="js-freshCm"></div>
  <div class="bfl-register">

    <div class="bfl-register-columns bfu-clear">

    </div>

  </div>

</div>

<div id="ambFooter"></div>

<img src="http://act.ameba.jp/blog/5166f6a6b2ee3727e70743f21584c5119313b3832983633353218393336092172602d7347657099313632328632333833113503e3814fe380a6e341bfe681a69fbd94e2991a0936" style="display:none" />
<img src="http://act.ameba.jp/common/4f66f516b3e43927910740f21e146c1555f521931f4380238463195322839e837d961f2692d7304657709626c676720656374737903687374733a232f606d6462656f256a762f6772672d7274667026" style="display:none" />

<img src="//ln.ameba.jp/v2/ra/sZofuVxH?qat=view&qv=1-15-0&qpi=article_blog-entry&qr=http%3A%2F%2Fameblo.jp%2Fari-step%2F&entry_id=%2212226218315%22&blogger_ameba_id=%22ari-step%22" style="display:none" />

<img src="http://ameblo.jp/accesslog/BlogAccessLog?bnm=ari-step&referAddr=http://ameblo.jp/ari-step/&skincode=wu_womanblog_50" alt="" class="accessLog" />

<img src="http://adt.measure.ameblo.jp/pc/ari-step/fb10e78f7474871ecee5a2515b1e49e93b0b1970" style="display:none;" />

<img src="//sy.ameblo.jp/sync/?org=sy.ameblo.jp" width="1" height="1" style="display:none;">


<script>
  window.ameblo = (typeof window.ameblo === 'object' && window.ameblo.nodeType !== 1) ? window.ameblo : {};
  window.ameblo.config = {
    urls: {
      ameblo: 'http://ameblo.jp',
      blog: 'http://blog.ameba.jp',
      blogNews: 'http://blognews.ameba.jp',
      official: 'http://official.ameba.jp',
      stat: 'http://stat100.ameba.jp',
      adcrossAPI: 'http://ad.pr.ameba.jp',
      iine:'http://iine.blog.ameba.jp',
      fresh: 'https://amebafresh.tv',
      abemaFresh: 'https://abemafresh.tv',
      hashtagAPI: 'http://rapi.blogtag.ameba.jp',
      hashtag: 'http://blogtag.ameba.jp'
    },
    flags: {
      isOfficial: false, 
      isTopBlogger: false,
      isEntryDetail: true,
      isEntryDetailEventJack: false
    },
    user: {
      amebaId: 'ari-step',
      groupCheckerId: 0,
      sex: '2',
      topBloggerCategoryId: '',
      nickname: 'Ari Ozawa'
    }
  };
</script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/common-1.1.2.js"></script>
<script>
new Amb.CommentBtnAmb.PcBlog({
setting:{
commentDomain:'http://comment.ameba.jp',
blogName:'ari-step',
smartPhoneSwitchFlg:'0'
}
});
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mustache.js/2.1.2/mustache.js"></script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/utils-1.0.0.js"></script>



<script src="http://stat100.ameba.jp/common_style/js/ameba/sp/common/sp.viewswitcher.js" charset="UTF-8"></script>


<script charset="UTF-8" src='http://stat100.ameba.jp/blog/js/newskin_imagelink-1.0.0.js'></script>

<script src='http://stat100.ameba.jp/blog/js/apm001.js'></script><script src='http://stat100.ameba.jp/adcross/pub/js/adLoader-0.1.3.js?20141105' type='text/javascript' charset='utf-8'></script>
<script type="text/javascript">
  new window.amb.adcross()
</script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/amebabar/ameblo.common.hf.1.4.0.js"></script>
<script src="http://stat100.ameba.jp/ameblo/pc/js/amebabar/ameba_centertext-1.2.0.js"></script>
<script src="http://stat100.ameba.jp/ameblo/pc/js/amebabar/amebabar-1.2.0.js"></script>
<script>
ameblo.amebabar.initialize({
type: 1,
centerText: {
id: 'barPickup',
callback: function(){ window.Amb.Ameblo.centertext.init(); }
}
});
</script>
<script src="http://stat100.ameba.jp/ameblo/pc/js/amebabar/footer_spm_link.1.0.0.js"></script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/entryDetailResize-1.1.0.js"></script>
<script>
new window.ameblo.EntryDetailResize({
  type: 'newskin'
});
</script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/freshSp-1.1.0.js"></script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/freshTopics-1.3.0.js"></script>

<script src="http://stat100.ameba.jp/ameblo/pc/js/freshCm-1.0.0.js"></script>




<script type="text/javascript" src="http://stat100.ameba.jp/ameblo/pc/js/bigfooter-1.11.0.js"></script>


<script charset="utf-8" src="http://stat100.ameba.jp/analytics/analytics_ameblo.js"></script>
<script type="text/javascript" src="http://stat100.ameba.jp/ameblo/pc/js/hashtag-1.7.0.js"></script>
<script src="http://stat100.ameba.jp/ameblo/pc/js/entryDetailEventJack-1.1.0.js"></script>


<script>
	var _fout_queue = _fout_queue || {}; if (_fout_queue.segment === void 0) _fout_queue.segment = {};
	if (_fout_queue.segment.queue === void 0) _fout_queue.segment.queue = [];

	_fout_queue.segment.queue.push({
		'user_id': 3949,
		'dat' : "radioactor"
	});

	(function() {
		var el = document.createElement('script'); el.type = 'text/javascript'; el.async = true;
		el.src = (('https:' == document.location.protocol) ? 'https://' : 'http://') + 'js.fout.jp/segmentation.js';
		var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(el, s);
	})();
</script></body>
</html>
'''
