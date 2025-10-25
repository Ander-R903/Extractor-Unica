from pathlib import Path

def create_gallery_html(tipos, imagenes, img_to_base64_func):    
    html_content = """
    <style>
    .gallery {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 10px;
    }
    .gallery img {
        border-radius: 8px;
        width: 150px;
        cursor: pointer;
        transition: transform 0.2s ease;
        border: 1px solid #ddd;
    }
    .gallery img:hover {
        transform: scale(1.05);
    }

    .modal {
        display: none;
        position: fixed;
        z-index: 9999;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.95);
        overflow: hidden;
    }

    .modal-container {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    .modal-content {
        max-width: 90%;
        max-height: 90%;
        border-radius: 6px;
        cursor: zoom-in;
        transition: transform 0.2s ease;
        transform-origin: center center;
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
    }

    .modal-content.zoomed {
        cursor: zoom-out;
        max-width: none;
        max-height: none;
    }

    .modal-caption {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        color: #fff;
        background-color: rgba(0,0,0,0.7);
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
    }

    .close {
        position: absolute;
        top: 20px;
        right: 35px;
        color: #fff;
        font-size: 40px;
        font-weight: bold;
        cursor: pointer;
        z-index: 10000;
        background-color: rgba(0,0,0,0.5);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }

    .close:hover {
        background-color: rgba(255,0,0,0.7);
    }

    .zoom-controls {
        position: absolute;
        top: 20px;
        left: 20px;
        display: flex;
        gap: 10px;
        z-index: 10000;
    }

    .zoom-btn {
        background-color: rgba(0,0,0,0.7);
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .zoom-btn:hover {
        background-color: rgba(255,255,255,0.3);
    }
    </style>

    <div class="gallery">
    """

    # Agregar las imágenes a la galería
    for tipo, img in zip(tipos, imagenes):
        if Path(img).exists():
            b64 = img_to_base64_func(img)
            html_content += f"""
            <div>
                <img src="data:image/png;base64,{b64}" alt="{tipo}" onclick="openModal('data:image/png;base64,{b64}', '{tipo}')">
                <p style='text-align:center; font-weight:bold;'>{tipo}</p>
            </div>
            """
        else:
            html_content += f"""
            <div>
                <p style='text-align:center; font-weight:bold;'>{tipo}</p>
                <p style='text-align:center; color:gray;'>(imagen no disponible)</p>
            </div>
            """

    # Agregar el modal y el JavaScript
    html_content += """
    </div>

    <div id="imgModal" class="modal">
        <div class="modal-container">
            <span class="close" onclick="closeModal()">&times;</span>
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomIn()">+</button>
                <button class="zoom-btn" onclick="zoomOut()">−</button>
                <button class="zoom-btn" onclick="resetZoom()">⟲</button>
            </div>
            <img class="modal-content" id="modalImage">
            <div class="modal-caption" id="caption"></div>
        </div>
    </div>

    <script>
    var currentScale = 1;
    var isDragging = false;
    var startX = 0, startY = 0, translateX = 0, translateY = 0;

    function openModal(src, caption) {
        var modal = document.getElementById("imgModal");
        var img = document.getElementById("modalImage");
        modal.style.display = "block";
        img.src = src;
        document.getElementById("caption").innerHTML = caption;
        resetZoom();
    }

    function closeModal() {
        document.getElementById("imgModal").style.display = "none";
        resetZoom();
    }

    function toggleZoom(e) {
        e.stopPropagation();
        if (currentScale === 1) {
            currentScale = 2;
            updateTransform();
        } else {
            resetZoom();
        }
    }

    function zoomIn() {
        currentScale = Math.min(currentScale + 0.5, 5);
        updateTransform();
    }

    function zoomOut() {
        currentScale = Math.max(currentScale - 0.5, 1);
        if (currentScale === 1) {
            translateX = 0;
            translateY = 0;
        }
        updateTransform();
    }

    function resetZoom() {
        currentScale = 1;
        translateX = 0;
        translateY = 0;
        updateTransform();
    }

    function updateTransform() {
        var img = document.getElementById("modalImage");
        img.style.transform = "translate(" + translateX + "px, " + translateY + "px) scale(" + currentScale + ")";
        if (currentScale > 1) {
            img.style.cursor = isDragging ? 'grabbing' : 'grab';
        } else {
            img.style.cursor = 'zoom-in';
        }
    }

    window.onload = function() {
        var modalImage = document.getElementById("modalImage");
        var clickTimeout = null;
        var hasMoved = false;
        
        modalImage.onmousedown = function(e) {
            hasMoved = false;
            
            if (currentScale > 1) {
                isDragging = true;
                startX = e.clientX - translateX;
                startY = e.clientY - translateY;
                modalImage.style.cursor = 'grabbing';
                e.preventDefault();
            } else {
                clickTimeout = setTimeout(function() {
                    clickTimeout = null;
                }, 200);
            }
        };

        document.onmousemove = function(e) {
            if (isDragging && currentScale > 1) {
                hasMoved = true;
                translateX = e.clientX - startX;
                translateY = e.clientY - startY;
                updateTransform();
            } else if (isDragging) {
                hasMoved = true;
            }
        };

        document.onmouseup = function(e) {
            if (isDragging) {
                isDragging = false;
                modalImage.style.cursor = currentScale > 1 ? 'grab' : 'zoom-in';
            }
        };

        modalImage.onclick = function(e) {
            if (!hasMoved && currentScale === 1) {
                toggleZoom(e);
            }
        };

        modalImage.onwheel = function(e) {
            e.preventDefault();
            
            if (e.deltaY < 0) {
                zoomIn();
            } else {
                zoomOut();
            }
        };

        document.onkeydown = function(e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                closeModal();
            }
        };
    };
    </script>
    """
    
    return html_content