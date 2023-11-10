const messageBox = document.querySelector('.message-box')
const closeBtn = document.querySelector('#close-btn')


closeBtn.addEventListener('click', ()=>{
    messageBox.style.display = 'none';
})

const YakaShow = document.querySelector('.search-engine-div-diem');
const btnJud = document.querySelector('.shasha-ka');

btnJud.addEventListener('click', ()=> {
    YakaShow.style.display = 'block';
})
