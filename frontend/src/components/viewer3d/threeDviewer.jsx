function ThreeDViewer() {

    return `

        <section class="viewer3d-section">

            <h2>
                Interactive 3D House Viewer
            </h2>

            <div class="viewer-container">

                <canvas id="house3DCanvas"></canvas>

            </div>

            <div class="viewer-buttons">

                <button>
                    Rotate
                </button>

                <button>
                    Zoom
                </button>

                <button>
                    Fullscreen
                </button>

            </div>

        </section>

    `;
}

export default ThreeDViewer;