from django.shortcuts import render, redirect, get_object_or_404
from usuarios.models import UsuarioCamp
from kbutzot.models import Kbutza, MadrijKbutza, Janij
from horarios.models import HorarioCamp
from transporte.models import Camion
from kbutzot.models import Kbutza
from transporte.models import Camion, CamionMadrij, CamionJanij
from django.http import HttpResponse
from django.contrib import messages
from transporte.models import Camion, CamionMadrij, CamionJanij, AsistenciaCamion, AsistenciaMadrijCamion
from media_camp.models import FotoCamp
from collections import defaultdict


from transporte.models import Camion

def inicio(request):
    camiones = Camion.objects.all()

    en_camino = camiones.filter(estado='en_camino').count()
    saliendo = camiones.filter(estado='saliendo').count()
    pendientes = camiones.filter(estado='pendiente').count()

    return render(request, 'inicio.html', {
        'en_camino': en_camino,
        'saliendo': saliendo,
        'pendientes': pendientes
    })


def panel_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')
    return render(request, 'panel_admin.html')


def madrijim(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if nombre and username and password:
            UsuarioCamp.objects.create(
                nombre=nombre,
                username=username,
                password=password,
                tipo='madrij'
            )
            return redirect('/panel-admin/madrijim/')

    lista_madrijim = UsuarioCamp.objects.filter(tipo='madrij')
    return render(request, 'madrijim.html', {'madrijim': lista_madrijim})


def detalle_madrij(request, madrij_id):
    madrij = get_object_or_404(UsuarioCamp, id=madrij_id, tipo='madrij')
    asignacion = MadrijKbutza.objects.filter(usuario=madrij).first()
    return render(request, 'detalle_madrij.html', {
        'madrij': madrij,
        'asignacion': asignacion
    })


def editar_madrij(request, madrij_id):
    madrij = get_object_or_404(UsuarioCamp, id=madrij_id, tipo='madrij')
    kbutzas = Kbutza.objects.all()
    asignacion = MadrijKbutza.objects.filter(usuario=madrij).first()

    if request.method == 'POST':
        madrij.nombre = request.POST.get('nombre')
        madrij.username = request.POST.get('username')
        madrij.password = request.POST.get('password')
        madrij.save()

        kbutza_id = request.POST.get('kbutza')
        if kbutza_id:
            kbutza = Kbutza.objects.get(id=kbutza_id)
            if asignacion:
                asignacion.kbutza = kbutza
                asignacion.save()
            else:
                MadrijKbutza.objects.create(usuario=madrij, kbutza=kbutza)

        return redirect(f'/panel-admin/madrijim/{madrij.id}/')

    return render(request, 'editar_madrij.html', {
        'madrij': madrij,
        'kbutzas': kbutzas,
        'asignacion': asignacion
    })


def eliminar_madrij(request, madrij_id):
    madrij = get_object_or_404(UsuarioCamp, id=madrij_id, tipo='madrij')

    if request.method == 'POST':
        madrij.delete()
        return redirect('/panel-admin/madrijim/')

    return render(request, 'eliminar_madrij.html', {'madrij': madrij})


def kbutzot_admin(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cuarto = request.POST.get('cuarto')

        if nombre:
            Kbutza.objects.create(
                nombre=nombre,
                cuarto=cuarto
            )
            return redirect('/panel-admin/kbutzot/')

    lista_kbutzot = Kbutza.objects.all().order_by('nombre')

    kbutzot_con_madrijim = []
    for k in lista_kbutzot:
        asignaciones = MadrijKbutza.objects.filter(kbutza=k)
        nombres_madrijim = [a.usuario.nombre for a in asignaciones]

        kbutzot_con_madrijim.append({
            'id': k.id,
            'nombre': k.nombre,
            'madrijim': nombres_madrijim
        })

    return render(request, 'kbutzot_admin.html', {'kbutzot': kbutzot_con_madrijim})


def detalle_kbutza(request, kbutza_id):
    kbutza = get_object_or_404(Kbutza, id=kbutza_id)
    janijim = Janij.objects.filter(kbutza=kbutza)
    madrijim_asignados = MadrijKbutza.objects.filter(kbutza=kbutza)
    madrijim_disponibles = UsuarioCamp.objects.filter(tipo='madrij')

    if request.method == 'POST':
        madrij_id = request.POST.get('madrij_id')
        if madrij_id:
            madrij = get_object_or_404(UsuarioCamp, id=madrij_id, tipo='madrij')
            existe = MadrijKbutza.objects.filter(usuario=madrij, kbutza=kbutza).first()
            if not existe:
                MadrijKbutza.objects.create(usuario=madrij, kbutza=kbutza)
        return redirect(f'/panel-admin/kbutzot/{kbutza.id}/')

    return render(request, 'detalle_kbutza.html', {
        'kbutza': kbutza,
        'janijim': janijim,
        'madrijim_asignados': madrijim_asignados,
        'madrijim_disponibles': madrijim_disponibles
    })


def editar_kbutza(request, kbutza_id):
    kbutza = get_object_or_404(Kbutza, id=kbutza_id)

    if request.method == 'POST':
        kbutza.nombre = request.POST.get('nombre')
        kbutza.cuarto = request.POST.get('cuarto')
        kbutza.save()
        return redirect(f'/panel-admin/kbutzot/{kbutza.id}/')

    return render(request, 'editar_kbutza.html', {'kbutza': kbutza})


def eliminar_kbutza(request, kbutza_id):
    kbutza = get_object_or_404(Kbutza, id=kbutza_id)
    kbutza.delete()
    return redirect('/panel-admin/kbutzot/')

def quitar_madrij_kbutza(request, kbutza_id, asignacion_id):
    asignacion = get_object_or_404(MadrijKbutza, id=asignacion_id, kbutza_id=kbutza_id)
    asignacion.delete()
    return redirect(f'/panel-admin/kbutzot/{kbutza_id}/')


def agregar_janij(request, kbutza_id):
    kbutza = get_object_or_404(Kbutza, id=kbutza_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')

        if nombre:
            Janij.objects.create(
                nombre=nombre,
                kbutza=kbutza
            )
            return redirect(f'/panel-admin/kbutzot/{kbutza.id}/')

    return render(request, 'agregar_janij.html', {'kbutza': kbutza})

def editar_janij(request, janij_id):
    janij = get_object_or_404(Janij, id=janij_id)
    kbutzas = Kbutza.objects.all().order_by('nombre')

    if request.method == 'POST':
        janij.nombre = request.POST.get('nombre')
        nueva_kbutza_id = request.POST.get('kbutza')

        if nueva_kbutza_id:
            janij.kbutza = get_object_or_404(Kbutza, id=nueva_kbutza_id)

        janij.save()
        return redirect(f'/panel-admin/kbutzot/{janij.kbutza.id}/')

    return render(request, 'editar_janij.html', {
        'janij': janij,
        'kbutzas': kbutzas
    })

def eliminar_janij(request, janij_id):
    janij = get_object_or_404(Janij, id=janij_id)
    kbutza_id = janij.kbutza.id
    janij.delete()
    return redirect(f'/panel-admin/kbutzot/{kbutza_id}/')


def actividades(request):
    return render(request, 'actividades.html')


def horarios(request):
    horarios = HorarioCamp.objects.all().order_by('dia', 'hora')

    horarios_por_dia = defaultdict(list)
    for h in horarios:
        horarios_por_dia[h.dia].append(h)

    return render(request, 'horarios.html', {
        'horarios_por_dia': dict(horarios_por_dia)
    })


def horarios_admin(request):
    if request.method == 'POST':
        dia = request.POST.get('dia')
        hora = request.POST.get('hora')
        actividad = request.POST.get('actividad')
        lugar = ""

        if dia and hora and actividad:
            HorarioCamp.objects.create(
                dia=dia,
                hora=hora,
                actividad=actividad,
                lugar=""
            )
            return redirect('/panel-admin/horarios/')

    horarios = HorarioCamp.objects.all().order_by('dia', 'hora')
    return render(request, 'horarios_admin.html', {'horarios': horarios})


def eliminar_horario(request, horario_id):
    horario = get_object_or_404(HorarioCamp, id=horario_id)
    horario.delete()
    return redirect('/panel-admin/horarios/')


def editar_horario(request, horario_id):
    horario = get_object_or_404(HorarioCamp, id=horario_id)

    if request.method == 'POST':
        horario.dia = request.POST.get('dia')
        horario.hora = request.POST.get('hora')
        horario.actividad = request.POST.get('actividad')
        horario.lugar = ""
        horario.save()
        return redirect('/panel-admin/horarios/')

    return render(request, 'editar_horario.html', {'horario': horario})


def fotos(request):
    return render(request, 'fotos.html')


def inscripciones(request):
    return render(request, 'inscripciones.html')


def transporte(request):
    return render(request, 'transporte.html')

def transporte_admin(request):
    madrijim = UsuarioCamp.objects.filter(tipo='madrij')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        estado = request.POST.get('estado')
        encargado_id = request.POST.get('encargado')
        hora_salida = request.POST.get('hora_salida')
        hora_estimada = request.POST.get('hora_estimada')
        link_ruta = request.POST.get('link_ruta')

        encargado = None
        if encargado_id:
            encargado = UsuarioCamp.objects.filter(id=encargado_id, tipo='madrij').first()

        if nombre and tipo and estado:
            Camion.objects.create(
                nombre=nombre,
                tipo=tipo,
                estado=estado,
                encargado=encargado,
                hora_salida=hora_salida,
                hora_estimada=hora_estimada,
                link_ruta=link_ruta
            )
            return redirect('/panel-admin/transporte/')

    camiones = Camion.objects.all().order_by('tipo', 'nombre')
    return render(request, 'transporte_admin.html', {
        'camiones': camiones,
        'madrijim': madrijim
    })

def editar_camion(request, camion_id):
    camion = get_object_or_404(Camion, id=camion_id)
    madrijim = UsuarioCamp.objects.filter(tipo='madrij')

    if request.method == 'POST':
        camion.nombre = request.POST.get('nombre')
        camion.tipo = request.POST.get('tipo')
        camion.estado = request.POST.get('estado')
        camion.hora_salida = request.POST.get('hora_salida')
        camion.hora_estimada = request.POST.get('hora_estimada')
        camion.link_ruta = request.POST.get('link_ruta')

        encargado_id = request.POST.get('encargado')
        camion.encargado = None
        if encargado_id:
            camion.encargado = UsuarioCamp.objects.filter(id=encargado_id, tipo='madrij').first()

        camion.save()
        return redirect('/panel-admin/transporte/')

    return render(request, 'editar_camion.html', {
        'camion': camion,
        'madrijim': madrijim
    })


def eliminar_camion(request, camion_id):
    camion = get_object_or_404(Camion, id=camion_id)
    camion.delete()
    return redirect('/panel-admin/transporte/')

def detalle_camion(request, camion_id):
    camion = get_object_or_404(Camion, id=camion_id)

    madrijim = CamionMadrij.objects.filter(camion=camion)
    janijim = CamionJanij.objects.filter(camion=camion)

    madrijim_disponibles = UsuarioCamp.objects.filter(tipo='madrij')
    janijim_disponibles = Janij.objects.all().order_by('nombre')

    if request.method == 'POST':
        tipo_form = request.POST.get('tipo_form')

        if tipo_form == 'madrij':
            madrij_id = request.POST.get('madrij_id')
            if madrij_id:
                madrij = get_object_or_404(UsuarioCamp, id=madrij_id, tipo='madrij')
                existe = CamionMadrij.objects.filter(camion=camion, madrij=madrij).first()
                if not existe:
                    CamionMadrij.objects.create(camion=camion, madrij=madrij)

        elif tipo_form == 'janij':
            janij_id = request.POST.get('janij_id')
            if janij_id:
                janij = get_object_or_404(Janij, id=janij_id)
                existe = CamionJanij.objects.filter(camion=camion, janij=janij).first()
                if not existe:
                    CamionJanij.objects.create(camion=camion, janij=janij)

        return redirect(f'/panel-admin/transporte/{camion.id}/')

    return render(request, 'detalle_camion.html', {
        'camion': camion,
        'madrijim': madrijim,
        'janijim': janijim,
        'madrijim_disponibles': madrijim_disponibles,
        'janijim_disponibles': janijim_disponibles,
    })

def quitar_janij_camion(request, camion_id, asignacion_id):
    asignacion = get_object_or_404(CamionJanij, id=asignacion_id, camion_id=camion_id)
    asignacion.delete()
    return redirect(f'/panel-admin/transporte/{camion_id}/')

def quitar_madrij_camion(request, camion_id, asignacion_id):
    asignacion = get_object_or_404(CamionMadrij, id=asignacion_id, camion_id=camion_id)
    asignacion.delete()
    return redirect(f'/panel-admin/transporte/{camion_id}/')


def quitar_kbutza_camion(request, camion_id, asignacion_id):
    asignacion = get_object_or_404(CamionJanij, id=asignacion_id, camion_id=camion_id)
    asignacion.delete()
    return redirect(f'/panel-admin/transporte/{camion_id}/')

def transporte_publico(request):
    camiones = Camion.objects.all().order_by('tipo', 'nombre')

    data = []

    for c in camiones:
        madrijim = CamionMadrij.objects.filter(camion=c)
        janijim = CamionJanij.objects.filter(camion=c)

        mapa_embed = None
        if c.link_ruta:
            mapa_embed = c.link_ruta

        data.append({
            'camion': c,
            'madrijim': madrijim,
            'janijim': janijim,
            'mapa_embed': mapa_embed,
        })

    return render(request, 'transporte_publico.html', {'data': data})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = UsuarioCamp.objects.filter(username=username, password=password).first()

        if usuario:
            request.session['usuario_id'] = usuario.id
            request.session['usuario_tipo'] = usuario.tipo

            if usuario.tipo == 'admin':
                return redirect('/panel-admin/')
            elif usuario.tipo == 'madrij':
                return redirect('/menu-madrij/')
            else:
                return redirect('/')

        return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('/')


def menu_madrij(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if not usuario_id or usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    camion_encargado = Camion.objects.filter(encargado=usuario).first()

    return render(request, 'menu_madrij.html', {
        'usuario': usuario,
        'camion_encargado': camion_encargado
    })

def transporte_madrij(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if not usuario_id or usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    camion_encargado = Camion.objects.filter(encargado=usuario).first()

    if request.method == 'POST' and camion_encargado:
        nuevo_estado = request.POST.get('estado')
        nueva_ruta = request.POST.get('link_ruta')

        janijim_camion = CamionJanij.objects.filter(camion=camion_encargado)
        madrijim_camion = CamionMadrij.objects.filter(camion=camion_encargado)

        requiere_lista = nuevo_estado in ['saliendo', 'en_camino']

        if requiere_lista:
            ids_janij_presentes = request.POST.getlist('janij_presentes')
            ids_madrij_presentes = request.POST.getlist('madrij_presentes')

            total_janijim = janijim_camion.count()
            total_madrijim = madrijim_camion.count()

            lista_incompleta = (
                (total_janijim > 0 and len(ids_janij_presentes) != total_janijim) or
                (total_madrijim > 0 and len(ids_madrij_presentes) != total_madrijim)
            )

            if lista_incompleta:
                data = []
                camiones = Camion.objects.all().order_by('tipo', 'nombre')
                for c in camiones:
                    madrijim = CamionMadrij.objects.filter(camion=c)
                    janijim = CamionJanij.objects.filter(camion=c)
                    data.append({
                        'camion': c,
                        'madrijim': madrijim,
                        'janijim': janijim
                    })

                return render(request, 'transporte_madrij.html', {
                    'usuario': usuario,
                    'camion_encargado': camion_encargado,
                    'data': data,
                    'janijim_encargado': janijim_camion,
                    'madrijim_encargado': madrijim_camion,
                    'error_lista': 'Debes pasar lista completa de janijim y madrijim antes de cambiar el estado.'
                })

            AsistenciaCamion.objects.filter(camion=camion_encargado).delete()
            AsistenciaMadrijCamion.objects.filter(camion=camion_encargado).delete()

            for item in janijim_camion:
                presente = str(item.janij.id) in ids_janij_presentes
                AsistenciaCamion.objects.create(
                    camion=camion_encargado,
                    janij=item.janij,
                    presente=presente
                )

            for item in madrijim_camion:
                presente = str(item.madrij.id) in ids_madrij_presentes
                AsistenciaMadrijCamion.objects.create(
                    camion=camion_encargado,
                    madrij=item.madrij,
                    presente=presente
                )

        camion_encargado.estado = nuevo_estado
        camion_encargado.link_ruta = nueva_ruta
        camion_encargado.save()

        return redirect('/transporte-madrij/')

    camiones = Camion.objects.all().order_by('tipo', 'nombre')

    data = []
    for c in camiones:
        madrijim = CamionMadrij.objects.filter(camion=c)
        janijim = CamionJanij.objects.filter(camion=c)

        data.append({
            'camion': c,
            'madrijim': madrijim,
            'janijim': janijim
        })

    janijim_encargado = []
    madrijim_encargado = []

    if camion_encargado:
        janijim_encargado = CamionJanij.objects.filter(camion=camion_encargado)
        madrijim_encargado = CamionMadrij.objects.filter(camion=camion_encargado)

    return render(request, 'transporte_madrij.html', {
        'usuario': usuario,
        'camion_encargado': camion_encargado,
        'data': data,
        'janijim_encargado': janijim_encargado,
        'madrijim_encargado': madrijim_encargado
    })

def fotos_publicas(request):
    fotos = FotoCamp.objects.all().order_by('-fecha_subida')
    return render(request, 'fotos_publicas.html', {'fotos': fotos})


def subir_foto(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if not usuario_id or usuario_tipo not in ['madrij', 'admin']:
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        archivos = request.FILES.getlist('archivos')

        for archivo in archivos:
            content_type = archivo.content_type

            if content_type.startswith('video/'):
                tipo = 'video'
            else:
                tipo = 'foto'

            FotoCamp.objects.create(
                titulo=titulo,
                archivo=archivo,
                tipo=tipo,
                subido_por=usuario
            )

        return redirect('/fotos/')

    return render(request, 'subir_foto.html')


def eliminar_foto(request, foto_id):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if not usuario_id:
        return redirect('/login/')

    foto = get_object_or_404(FotoCamp, id=foto_id)

    puede_eliminar = (
        usuario_tipo == 'admin' or
        (foto.subido_por and foto.subido_por.id == usuario_id)
    )

    if not puede_eliminar:
        return redirect('/fotos/')

    if request.method == 'POST':
        foto.delete()
        return redirect('/fotos/')

    return redirect('/fotos/')

def kbutzot_publicas(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    mi_kbutza = None

    if usuario_id and usuario_tipo == 'madrij':
        usuario = UsuarioCamp.objects.filter(id=usuario_id, tipo='madrij').first()
        if usuario:
            asignacion = MadrijKbutza.objects.filter(usuario=usuario).first()
            if asignacion:
                mi_kbutza = asignacion.kbutza

    kbutzot = Kbutza.objects.all().order_by('nombre')

    data = []
    for k in kbutzot:
        madrijim = MadrijKbutza.objects.filter(kbutza=k)
        janijim = Janij.objects.filter(kbutza=k)

        data.append({
            'kbutza': k,
            'madrijim': madrijim,
            'janijim': janijim
        })

    mi_madrijim = []
    mi_janijim = []

    if mi_kbutza:
        mi_madrijim = MadrijKbutza.objects.filter(kbutza=mi_kbutza)
        mi_janijim = Janij.objects.filter(kbutza=mi_kbutza)

    return render(request, 'kbutzot_publicas.html', {
        'data': data,
        'mi_kbutza': mi_kbutza,
        'mi_madrijim': mi_madrijim,
        'mi_janijim': mi_janijim
    })