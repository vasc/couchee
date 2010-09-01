$(document).ready(function() {
        var s = $('.stars');
        var couch_path = "M0,43v60q0,20,20,20h190q20,0,20-20v-60q0-20-20-20h-5a32,32-50,0,0,-50-15a30,30-50,0,0-40,0a30,30-50,0,0-40,0a32,32-50,0,0-50,15h-5q-20,0-20,20zM35,58h160v5h-160z"
        var path = "M15.999,22.77l-8.884,6.454l3.396-10.44l-8.882-6.454l10.979,0.002l2.918-8.977l0.476-1.458l3.39,10.433h10.982l-8.886,6.454l3.397,10.443L15.999,22.77L15.999,22.77z"
        s.css('display', 'none');
        var logo = Raphael($('#logo')[0], 69, 37)
        var couch = logo.path(couch_path).attr({fill: "#f3f3f3", stroke: "none"})
        //logo.text(140, 21, "coucheeb").attr({"class":"logo",fill:"#dfdfdf"})
        couch.scale(0.3, 0.3, 0, 0)
        
        //$('#filters').hover(
        //  function() {$(this).animate({'height': "20"})},
        //  function() {$(this).animate({'height': "0"})});
        
        for(var e in s.get()){
          var l = s[e];
          var t = $('<span class="viz"></span>');
          s.eq(e).before(t);
          
          text = s.eq(e).text()
          if (text == '' || text == ' ') continue;
          
          text = text.split(" ", 2);
          
          var votes = parseInt(text[1])
          if(votes < 1000) rvotes = 0
          else if(votes < 6000) rvotes = 1
          else if(votes < 12000) rvotes = 2
          else if(votes < 20000) rvotes = 3
          else if(votes < 33000) rvotes = 4
          else rvotes = 5
          
          
          var stars = parseFloat(text[0]) / 2
          var full_star_count = Math.floor(stars)
          var partial_star_percent = Math.floor((stars - full_star_count) * 100)
          //console.log(full_star_count + " " + partial_star_percent)
          var r = Raphael(t[0], 60, 24)
          //console.log($(l).text())
          
          for(var i = 0; i < full_star_count; i++){
            var p = r.path(path).attr({fill: "#808080", stroke: "#808080", "stroke-width": 1});
            p.scale(0.30, 0.30, 0, 0)
            p.translate(i*12, 0)
          }
          
          var p = r.path(path).attr({fill: "0-#808080-#808080:"+partial_star_percent+"-#fff:"+partial_star_percent+"-#fff", stroke: "#808080", "stroke-width": 0.5});
          p.scale(0.30, 0.30, 0, 0)
          p.translate(full_star_count*12, 0)
          
          for(var i = full_star_count; i < 5; i++){
            var p = r.path(path).attr({fill: "none", stroke: "#808080", "stroke-width": 0.3});
            p.scale(0.30, 0.30, 0, 0)
            p.translate(i*12, 0)
          }
          
          
          for(var i = 0; i < 5; i++){
            if(i < rvotes) fill = "#808080";
            else fill = "none"
            var p = r.rect(0.5, 15.5, 10, 6, 2).attr({fill: fill, stroke: "#808080", "stroke-width": 0.5});
            p.translate(i*12, 0)
          }
          
          $('.button').css('visibility', 'hidden');
          $('.button').parent().hover(
              function(){ $(this).children('.button').css('visibility', ''); },
              function(){ $(this).children('.button').css('visibility', 'hidden'); }
          )
          
          
        }
      });
