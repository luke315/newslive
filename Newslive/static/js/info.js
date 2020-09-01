// $(function(){
//     $('#share').share({sites: ['qzone', 'qq', 'weibo','wechat']});
// })
 
$(function(){
    $('#share').share({sites: ['qzone', 'qq', 'weibo','wechat']});
    // live_detail();
    $(".fengxiang img").click(function(){
        var str='<div class="tip"> 长按[保存卡片] 或 [发送给朋友] </div>';
        $("#fengxiangModal").show();
        htmlToImage(document.getElementById("fengxiangModal"), function (dataUrl) {
            var newImg = document.createElement("img");
            newImg.src = dataUrl;  
            $("#fengxiangModal").hide();
            $("#fengxiangModal2").show();
            $("#fengxiangModal2").empty().append(str).append(newImg);
            $("#fengxiangModal2 img").css("width", "100%"); 

           
            $("#fengxiangModal2").click(function(){
                $("#fengxiangModal2").hide();
            })
        })
    })
    
}) 

function live_detail(){
    var tag_id=getUrlParam("tag_id");
    var theme_id=getUrlParam("theme_id");
    var data = {
        tag_id: tag_id,
        theme_id:theme_id
    }
    console.log("參數：",data)
    $.post('/live/page_detail/', data, function (datas) {
        console.log(datas)
        if(datas.results){
            $("#datetime1").html(datas.results.theme_data.theme_time);
            $("#datetime2").html(datas.results.theme_data.theme_time);
            $("#rich_text1").html(datas.results.theme_data.rich_text);
            $("#rich_text2").html(datas.results.theme_data.rich_text);
            if(datas.results.theme_data.img){
                $("#img1").show();
                $("#img2").show();
                $("#img1 img").attr("src",datas.results.theme_data.rich_text);
                $("#img2 img").attr("src",datas.results.theme_data.rich_text);
            }else{
                $("#img1").hide();
                $("#img2").hide();
            }
            // $("#rich_text1").html(datas.results.theme_data.rich_text);
            // $("#rich_text2").html(datas.results.theme_data.rich_text);
        }
        //theme_data.list
    }).error(function (xhr, status, info) {


    });
}

/*
功能：HTML页面保存Base64图片并上传到服务器，返回上传图片信息
实例：
说明：
*/
function htmlToImage(element, callback) {

    // var width = element.clientWidth;
    // var height = element.clientHeight;
    var width = element.scrollWidth;
    // var height = element.scrollHeight;
    // var width = element.offsetWidth;
    var height = document.getElementById("imghead").offsetHeight + document.getElementById("imgcontent").offsetHeight;
    console.log(height)
    var scale = 2;
    var canvas = document.createElement("canvas");
    // 获取元素相对于视窗的偏移量
    var rect = element.getBoundingClientRect();
    canvas.width = width * scale;
    canvas.height = height * scale;
    var context = canvas.getContext("2d");
    context.scale(scale, scale);

    // 设置context位置, 值为相对于视窗的偏移量的负值, 实现图片复位
    context.translate(-rect.left, -rect.top);

    var options = {
        scale: scale,
        canvas: canvas,
        // logging: true,
        width: width,
        height: height,
        taintTest: true, //在渲染前测试图片
        useCORS: true, //貌似与跨域有关，但和allowTaint不能共存
        dpi: window.devicePixelRatio, // window.devicePixelRatio是设备像素比
        background: "#fff",
        // taintTest: false,
        // allowTaint: true, 
        foreignObjectRendering: true
    };
 
    html2canvas(element, options).then(function (canvas) {
        var dataURL = canvas.toDataURL('image/png', 1.0); //将图片转为base64, 0-1 表示清晰度
        //var base64String = dataURL.toString().substring(dataURL.indexOf(",") + 1); //截取base64以便上传


        callback(dataURL);
    });

}