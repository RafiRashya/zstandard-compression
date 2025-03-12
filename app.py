from flask import Flask, request, render_template, send_file
import os
import zstandard as zstd

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"
DECOMPRESSED_FOLDER = "decompressed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
os.makedirs(DECOMPRESSED_FOLDER, exist_ok=True)

def get_file_size(file_path):
    return round(os.path.getsize(file_path) / 1024, 2)

def compress_file(input_path, output_path):
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        compressor = zstd.ZstdCompressor()
        f_out.write(compressor.compress(f_in.read()))

def decompress_file(input_path, output_path):
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        compressor = zstd.ZstdDecompressor()
        f_out.write(compressor.decompress(f_in.read()))

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            compressed_path = os.path.join(COMPRESSED_FOLDER, os.path.splitext(file.filename)[0] + '.zst')
            file.save(file_path)

            # Kompresi file
            compress_file(file_path, compressed_path)

            # Hitung ukuran file sebelum & sesudah
            original_size = get_file_size(file_path)
            compressed_size = get_file_size(compressed_path)

            compression_ratio = round((1 - (compressed_size / original_size)) * 100, 2)

            return render_template("index.html", original_size=original_size, compressed_size=compressed_size, compressed_path=os.path.basename(compressed_path), compression_ratio=compression_ratio)
    
    return render_template("index.html", original_size=None, compressed_size=None, compressed_path=None)

@app.route("/download-compressed/<filename>")
def download_compressed_file(filename):
    file_path = os.path.join(COMPRESSED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

@app.route("/download-decompressed/<filename>")
def download_decompressed_file(filename):
    file_path = os.path.join(DECOMPRESSED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

@app.route("/decompress", methods=['POST'])
def decompress():
    file = request.files['file']
    if file:
        compressed_path = os.path.join(UPLOAD_FOLDER, file.filename)
        decompressed_path = os.path.join(DECOMPRESSED_FOLDER, file.filename).replace(".zst", "")

        file.save(compressed_path)

        decompress_file(compressed_path, decompressed_path)
        decompressed_size = get_file_size(decompressed_path)

        return render_template("index.html", decompressed_path=os.path.basename(decompressed_path), decompressed_size=decompressed_size)

if __name__ == "__main__":
    app.run(debug=True)