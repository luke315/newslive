var tagIndex = 0;
var pageIndex=0;
var loadingStep = 0; //加载状态0默认，1显示加载状态，2执行加载数据，只有当为0时才能再次加载，这是防止过快拉动刷新  
var dataMore = false;
var myScroll=null;
var pullUp=null;
var page_theme_id=null;
$(function () {
    pageIndex=0;
    
    pullUp = $("#pullUp");
    var  pullDown = $("#pullDown"), 
        pullDownLabel = $(".pullDownLabel"),
        pullUpLabel = $(".pullUpLabel"),
        container = $('#list');
          

    // pullDown.hide();
    // if (pageIndex == 1) {
    //     // pullUp.hide()
    //     pullUp.removeClass("refresh").addClass("loading");
    //     pullUpLabel.text("加载中...");
    // };
    tag_dom();
    myScroll = new IScroll("#wrapper", {
        scrollbars: true,
        mouseWheel: true,
        click : false ,
        preventDefault: false,//（把这句加上去哦） 这里是重点
        interactiveScrollbars: true,
        shrinkScrollbars: 'scale',
        fadeScrollbars: true,
        scrollY: true,
        probeType: 2,
        bindToWrapper: true
    });
    live_page();
    myScroll.on("scroll", function () { 
        if (loadingStep == 0 && !pullUp.attr("class").match('refresh')) { 
            if (this.y < (this.maxScrollY - 20)) { //上拉加载更多   
                pullUp.addClass("refresh").show();
                pullUpLabel.text("松手加载新数据");
                loadingStep = 1;
                myScroll.refresh();
            }
        }
    });
    myScroll.on("scrollEnd", function () {
        if (dataMore) {
            if (loadingStep == 1) {
                if (pullUp.attr("class").match("refresh")) { //下拉刷新操作  
                   
                    pullUp.removeClass("refresh").addClass("loading");
                    pullUpLabel.text("加载中...");
                    loadingStep = 2;
                    // pullUpAction(); 
                    live_page()
                }
            }
        } else {
            pullUp.addClass("refresh").show();
            pullUpLabel.empty().append('你触碰到底线了，亲');
        }
    });

     
     window.setInterval("page_update()",15000);//定时执行
})

function live_page() {
    pageIndex=pageIndex+1;
    var tag_id=getUrlParam("tag_id");
    if(!tag_id){ 
        tag_id="0";
    }
    //tagIndex=tag_id;
    var data = {
        tag_id: tag_id,
        page:pageIndex
    } 
    if(page_theme_id){
        data.page_theme_id=page_theme_id;
    }
    console.log(data)
    $.post('/live/page/', data, function (datas) {
        console.log(datas) 
        
        list_dom(datas.results.theme_data.list,false) 
    }).error(function (xhr, status, info) { 
    });

}

function tag_dom() {
    var tag_id=getUrlParam("tag_id");
    if(!tag_id){ 
        tag_id="0";
    } 
    $("#tag"+tag_id).addClass("active")
    var widthHelf=($('.container .tags').outerWidth(true))/2;
    var tagLeft=$("#tag"+tag_id).offset().left;
    var tagWidthHelf=$("#tag"+tag_id).outerWidth(true)/2;
    // console.log(tagLeft -widthHelf+tagWidthHelf);
    // console.log(tagLeft,widthHelf,tagWidthHelf);
    $('.container .tags').scrollLeft(tagLeft -widthHelf+tagWidthHelf)
    // if(tagLeft>widthHelf){
    //     $('.container .tags').animate({ 
    //         scrollLeft: tagLeft -widthHelf+tagWidthHelf
    //     }, 500 );
    // }else{

    // }
    
    $(".container .tags div").click(function(){ 
        location.href="/live/index/?tag_id="+$(this).data("index");
        // live_page();
    })
}

function list_dom(datas,isLoop) {
    var dom = "";
    var date = ""; 
    datas.forEach((item,index) => {
        if(pageIndex===1 && index == 0){
            page_theme_id=item.theme_id;
            
        } 
        var dateTime = item.theme_time.split(" ");
       
        if (dateTime.length >= 2 && date != dateTime[0] && (dateTime[0] != $("#scroller .items .item2").last().html())) {
            
            date = dateTime[0];
            dom = dom + '<div class="item2">' + date + '</div>';
        }
        var img='';
        if(item.img){
            img = '<div class="imgs">' +
            '<img src="'+item.img_data+'" onerror="this.style.display=\'none\'"/>' +
            '</div>'
        }
        //onerror="this.style.display=\'none\'"
        dom = dom + '<div class="item" data-tagid="'+item.tag_id+'" data-themeid="'+item.theme_id+'"> <div class="spot"> </div>' +
            '<div class="time">' + dateTime[1] + '</div>' +
            '<div class="content">' +
            item.rich_text + img +
            '</div>' + '</div>'
    });
   
    if(isLoop){
        if(date == $("#scroller .items .item2").first().html()){
            $("#scroller .items .item2")[0].remove();
        }
        $("#scroller .items").prepend(dom); 
    }else{
       
        $("#scroller .items").append(dom);
         
        if(datas.length<15){
            dataMore=false;
        }else{
            loadingStep = 0;
            dataMore=true;
            pullUp.removeClass("refresh").removeClass("loading").hide();
        } 
    }
    $("#scroller .items .item").click(function(){ 
        location.href="/live/index_detail/?tag_id="+$(this).data("tagid")+"&theme_id="+$(this).data("themeid");
    })
   
    
    myScroll.refresh();
    
}

function page_update(){
  
    var tag_id=getUrlParam("tag_id");
    if(!tag_id){ 
        tag_id="0";
    }
    //tagIndex=tag_id;
    var data = {
        tag_id: tag_id, 
    } 
    console.log("page_update",data)
    if(page_theme_id){
        data.page_theme_id=page_theme_id;
    
        console.log("page_update",data)
        $.post('/live/page_update/', data, function (datas) {
            console.log(datas) 
            if(datas.results){
                list_dom(datas.results.theme_data.list,true) 
            }
        }).error(function (xhr, status, info) { 
        });
    }

}