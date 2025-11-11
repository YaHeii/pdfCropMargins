import uvicorn
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
# docker 环境下配置文件
# 导入 pdfCropMargins 的核心逻辑
try:
    from pdfCropMargins.pdfCropMargins import main as pdfCropMargins_main
except ImportError:
    print("错误：请确保 pdfCropMargins 已经安装或在 Python 路径中")
    exit(1)

app = FastAPI()

@app.post("/crop-pdf/")
async def crop_pdf_endpoint(file: UploadFile = File(...)):
    """
    接收一个 PDF 文件，裁剪它，然后返回裁剪后的文件。
    """
    # 1. 创建一个临时目录来处理文件
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = f"{temp_dir}/input.pdf"
        output_path = f"{temp_dir}/output.pdf"

        # 2. 保存上传的文件
        try:
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"保存文件失败: {e}")
        finally:
            file.file.close()

        # 3. 准备调用 pdfCropMargins 的参数
        # 我们将模拟命令行参数
        # 示例：运行 "pdfCropMargins -o output.pdf input.pdf"
        cli_args = [
            "pdfCropMargins", # 脚本名，占位符
            "-o", output_path,
            input_path
            # 你可以在这里添加更多固定参数，或通过查询参数从前端接收
        ]

        # 4. 调用核心裁剪逻辑
        try:
            # pdfCropMargins_main() 返回一个退出码
            exit_code = pdfCropMargins_main(cli_args)
            if exit_code != 0:
                raise HTTPException(status_code=500, detail=f"pdfCropMargins 处理失败，退出码: {exit_code}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"裁剪过程中出错: {e}")

        # 5. 返回处理后的文件
        return FileResponse(
            path=output_path,
            media_type='application/pdf',
            filename="cropped.pdf"
        )

@app.get("/")
def read_root():
    # 我们可以顺便提供一个超简单的 HTML 前端
    html_content = """
    <html>
        <head><title>PDF Cropper</title></head>
        <body>
            <h2>PDF 边距裁剪器 (pdfCropMargins)</h2>
            <form action="/crop-pdf/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept="application/pdf">
                <input type="submit" value="上传并裁剪">
            </form>
        </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # 运行时使用： uvicorn server:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)