from django.shortcuts import render
from django.db import connection

def _fetchall(q, params=None):
    with connection.cursor() as cur:
        cur.execute(q, params or [])
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

def home(request):
    return render(request, 'index.html')

def notas_view(request):
    # lista de cursos
    cursos = _fetchall("""
        SELECT CursoID, NombreCurso
        FROM dbo.Curso
        ORDER BY NombreCurso
    """)

    curso_id = request.GET.get('curso')  # string o None
    bimestre = request.GET.get('bimestre')  # "1".."4" o None

    filas = []
    curso_nombre = None

    if curso_id:
        # nombre del curso
        row = _fetchall("SELECT NombreCurso FROM dbo.Curso WHERE CursoID = %s", [curso_id])
        curso_nombre = row[0]['NombreCurso'] if row else None

        # pivot por bimestre + promedio
        filas = _fetchall("""
            SELECT
                e.Nombre AS Nombre,
                MAX(CASE WHEN n.BimestreID = 1 THEN n.Nota END) AS I,
                MAX(CASE WHEN n.BimestreID = 2 THEN n.Nota END) AS II,
                MAX(CASE WHEN n.BimestreID = 3 THEN n.Nota END) AS III,
                MAX(CASE WHEN n.BimestreID = 4 THEN n.Nota END) AS IV,
                AVG(CAST(n.Nota AS DECIMAL(5,2))) AS Promedio
            FROM dbo.Nota n
            JOIN dbo.Estudiante e ON e.EstudianteID = n.EstudianteID
            WHERE n.CursoID = %s
            GROUP BY e.Nombre
            ORDER BY e.Nombre;
        """, [curso_id])

    ctx = {
        'cursos': cursos,
        'curso_id': int(curso_id) if curso_id else None,
        'curso_nombre': curso_nombre,
        'filas': filas,
        'bimestre': int(bimestre) if bimestre else None,
    }
    return render(request, 'notas.html', ctx)
