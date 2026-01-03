window.addEventListener('load', ()=>{
    // $.ajax({
    //     type: 'post',
    //     url: '/catch/info',
    //     contentType: 'application/json; charset=utf-8',
    //     success: e=>{
    //         ctx.canvas.width = e[0];
    //         ctx.canvas.height = e[1];
    //         screen = e;
    //         resize()
    //     }
    // }); 

    screen = [1366, 768];
    ctx.canvas.width = screen[0];
    ctx.canvas.height = screen[1];
    resize()
})
window.addEventListener('resize', resize)

const canvas = document.getElementById('canvas');
const canvas_touch_event = new Hammer(canvas)
canvas_touch_event.get('pan').set({direction:Hammer.DIRECTION_ALL})
canvas_touch_event.get('pinch').set({enable: true})

const ctx = canvas.getContext('2d',{ willReadFrequently: true });
const brushSize = document.getElementById('scale')
let cor = { x:0 , y:0 };
let down = false;
let drag = false;
let touched = true;
let changes = []
let scales = [0.25,0.5,0.75,1,2,3,4,5];
let screen = []
var img = new Image()

let brush = document.getElementById('drag')
var last_canvas_posX=0, last_canvas_posY=0,Scale=1, canvas_posX=0, canvas_posY=0, canvas_last_scale=1, last_rotation=0, canvas_rotation
var heading = $('h1')
var times;

function resize() {
    canvas_last_scale =innerWidth/screen[0];
    canvas.style.top = (innerHeight/canvas_last_scale-screen[1])/2 + 'px'
    canvas.style.transformOrigin = 'left top';
    canvas.style.zoom = canvas_last_scale;
    last_canvas_posX=parseInt(getComputedStyle(canvas).left), last_canvas_posY= (innerHeight/canvas_last_scale-screen[1])/2
}



function post(url, data="", callback=""){
       $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success: callback
    });
}

timeStamp = 0
//Event Handler ||Touch Start||
document.addEventListener('touchstart', e => {
    if (e.target == canvas && e.touches.length<2 && touched) {
        // last_rotation = parseInt(offset.rotate)
        var x = (e.touches[0].clientX)/canvas_last_scale-canvas_posX
        var y = (e.touches[0].clientY)/canvas_last_scale-canvas_posY
        // var ang = Math.atan(y/x)-last_rotation*Math.PI/180
        // var r = Math.sqrt(x*x+y*y)
        // x = r*Math.cos(ang); y=r*Math.sin(ang)
        // heading.text()
        cor.x = x; cor.y = y
        if (cor.x && cor.y && drag) {
            changes.push(ctx.getImageData(0, 0, canvas.width, canvas.height))
            if (changes.length > 10) changes.shift();


            // ~~~~~~~~~~~~~~~SEND TO SERVER~~~~~~~~~~~~~~~~~~//
            post('/catch/touchstart', {
                'value': [cor.x, cor.y]
            })
            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
        }

        if(!drag && (e.timeStamp-timeStamp) <= 300){
            down = true;
            post('/catch/mousedown');
        }
        timeStamp = e.timeStamp;
    }
})
//Event Handler ||Touch End||
canvas.addEventListener('touchend', e => {
    if (down||drag) {
        down = false;
        // ~~~~~~~~~~~~~~~SEND TO SERVER~~~~~~~~~~~~~~~~~~//
        post('/catch/touchend', "",(b)=>{
            
            img.src = 'data:image/jpeg;base64, '+b;
            img.onload = ()=>{ctx.drawImage(img,0,0,canvas.width, canvas.height)}

        });
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//

    }
})

var tip = $('#tip') //Event Handler ||Touch Move||
canvas.addEventListener('touchmove', e => {
    if(e.touches.length<2 && touched){

    var x = (e.touches[0].clientX)/canvas_last_scale-canvas_posX
    var y = (e.touches[0].clientY)/canvas_last_scale-canvas_posY
    // var ang = Math.atan(y/x)-last_rotation*Math.PI/180
    // var r = Math.sqrt(x*x+y*y);
    // x = r*Math.cos(ang); y=r*Math.sin(ang)
    draw(x, y);
    }
});
// canvas.addEventListener('mousemove',e=>{draw(e.clientX, e.clientY)});

function draw(x, y) {
    if (drag) {
        ctx.beginPath();
        ctx.lineWidth = brushSize.value;
        ctx.lineCap = 'round';
        ctx.strokeStyle = 'green';
        ctx.moveTo(cor.x, cor.y);
        ctx.lineTo(x, y);
        // ctx.moveTo(cor.x, cor.y - y * (80 / canvas.height));
        // ctx.lineTo(x, y - y * (80 / canvas.height));
        ctx.stroke();
        
        // t.text(cor.x+" "+x)
    }
    // ~~~~~~~~~~~~~~~SEND TO SERVER~~~~~~~~~~~~~~~~~~//
    post('/catch/pos', {
                'value': [(x - (drag ? 0 : cor.x)), (y - (drag ? 0 : cor.y))]
            });
    // post('/catch/pos', {
    //             'value': [(x - (drag ? init[0] : cor.x)) * scales[scale.value], (y - (drag ? init[1] : cor.y)) * scales[scale.value]]
    //         });
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
    cor.x = x; cor.y = y;
}


document.getElementById('erase').addEventListener('click', () =>{ctx.clearRect(0, 0, canvas.width, canvas.height);});

brush.addEventListener('click', (e) => {
    if (drag) {
        drag = false;
        brush.classList.remove('active');
        init = undefined
    } else {
        drag = true;
        brush.classList.add('active');
    }
    post('catch/drag/' + (drag ? 1 : 0),"",(b)=>{
        if(drag){
            img.src = 'data:image/jpeg;base64, '+b;
            img.onload = ()=>ctx.drawImage(img,0,0,canvas.width, canvas.height)
            // canvas.style.backgroundImage="linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('data:image/jpeg;base64, "+b+"')";
        }
        // console.log(""+btoa(e))
        
    })
})

document.getElementById('undo').addEventListener('click', () => {
    post('/catch/undo');
    if(changes.length) ctx.putImageData(changes.pop(), 0, 0);
})


document.querySelector('.start').addEventListener('click', e=>{
    document.documentElement.requestFullscreen();
    e.target.style.display = 'none';
})
var rotation;
canvas_touch_event.on('rotate pinch pinchstart pinchend', e=>{
    switch(e.type){
        case 'pinchstart':
            touched = false;
            clearTimeout(times)
            // canvas_posX = e.deltaX
            // canvas_posY = e.deltaY
            // Scale = e.scale
            // last_rotation = parseInt(offset.rotate)
            rotation = e.rotation
            // last_canvas_posX = parseInt(offset.left)
            // last_canvas_posY = parseInt(offset.top)
            break;
        case 'pinch': 
            // canvas.style.transformOrigin = (e.center.x/canvas_last_scale)+"px "+(e.center.y/canvas_last_scale)+"px";
            Scale = canvas_last_scale*e.scale;
            // canvas_rotation = last_rotation+(e.rotation-rotation);
            canvas_posX = last_canvas_posX+(e.center.x*(1-e.scale)+e.deltaX)/Scale;
            canvas_posY = last_canvas_posY+(e.center.y*(1-e.scale)+e.deltaY)/Scale;
            canvas.style.left = canvas_posX+'px';
            canvas.style.top = canvas_posY+'px';
            canvas.style.zoom =Scale ;
            // t.text((e.center.y/canvas_last_scale-last_canvas_posY)*(1-e.scale))
            // heading.text(e.center.x, e.center.y)
            // canvas.style.rotate = canvas_rotation+'deg';
            // tip.css({left:(e.center.x)-5, top:(e.center.y)-5});
            break;
        case 'pinchend':
            canvas_last_scale = Scale;
            last_canvas_posX = canvas_posX;
            last_canvas_posY = canvas_posY;
            // last_rotation = canvas_rotation;
            times = setTimeout(()=>{touched = true}, 500)
            
            break;      
        }
    
})


    console.log(canvas_touch_event)