from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/ffmpeg', methods=['POST'])
def execute_ffmpeg():
    try:
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'Missing command parameter'}), 400

        # Execute the FFmpeg command
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
