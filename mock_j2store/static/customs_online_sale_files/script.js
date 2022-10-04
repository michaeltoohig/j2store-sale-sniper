/**
 * ------------------------------------------------------------------------
 * JA Healthcare Template
 * ------------------------------------------------------------------------
 * Copyright (C) 2004-2018 J.O.O.M Solutions Co., Ltd. All Rights Reserved.
 * @license - Copyrighted Commercial Software
 * Author: J.O.O.M Solutions Co., Ltd
 * Websites:  http://www.joomlart.com -  http://www.joomlancers.com
 * This file may not be redistributed in whole or significant part.
 * ------------------------------------------------------------------------
*/

 (function($){

  $(window).on('load',function () {
    ////////////////////////////////
    // equalheight for col
    ////////////////////////////////
    var ehArray = ehArray2 = [],
      i = 0;

    $('.equal-height').each (function(){
      var $ehc = $(this);
      if ($ehc.has ('.equal-height')) {
        ehArray2[ehArray2.length] = $ehc;
      } else {
        ehArray[ehArray.length] = $ehc;
      }
    });
    for (i = ehArray2.length -1; i >= 0; i--) {
      ehArray[ehArray.length] = ehArray2[i];
    }

    var equalHeight = function() {
      for (i = 0; i < ehArray.length; i++) {
        var $cols = ehArray[i].children().filter('.col'),
          maxHeight = 0,
          equalChildHeight = ehArray[i].hasClass('equal-height-child');

      // reset min-height
        if (equalChildHeight) {
          $cols.each(function(){$(this).children().css('min-height', 0)});
        } else {
          $cols.css('min-height', 0);
        }
        $cols.each (function() {
          maxHeight = Math.max(maxHeight, equalChildHeight ? $(this).children().innerHeight() : $(this).innerHeight());
        });
        if (equalChildHeight) {
          $cols.each(function(){
            $(this).children().css('min-height', maxHeight);
      });
        } else {
          $cols.css('min-height', maxHeight);
        }
      }
      // store current size
      $('.equal-height > .col').each (function(){
        var $col = $(this);
        $col.data('old-width', $col.width()).data('old-height', $col.innerHeight());
      });
    };

    equalHeight();

    // monitor col width and fire equalHeight
    setInterval(function() {
      $('.equal-height > .col').each(function(){
        var $col = $(this);
        if (($col.data('old-width') && $col.data('old-width') != $col.width()) ||
            ($col.data('old-height') && $col.data('old-height') != $col.innerHeight())) {
          equalHeight();
          // break each loop
          return false;
        }
      });
  }, 500);
  });

  // Add Inview
  $(document).ready(function () {
    if($('.enable-effect').length > 0) {
      $('.section-wrap > div,.t3-sl-1,.blog.blog-department,div.categories-list').bind('inview', function(event, visible) {
        if (visible) {
          $(this).addClass('ja-inview');
        }
      });
    }
  });

  // Add Affix to JA MainMenu
  $(document).ready(function () {
    if($('#t3-mainnav').length > 0) {
      $('#t3-mainnav').affix({
        offset: {
          top: $('#t3-header').outerHeight() + $('.t3-top-bar').outerHeight()
        }
      });
    }
  });


  $(document).ready(function () {
    $("#addthis-wrap .btn").click(function(){
      $("#addthis-wrap .addthis_inline_follow_toolbox").toggle();
    });
  });
})(jQuery);

//Fix bug tab typography
(function($){
  $(document).ready(function(){
    if($('.docs-section .nav.nav-tabs').length > 0){
      $('.docs-section .nav.nav-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
            });
    }
  });
})(jQuery);