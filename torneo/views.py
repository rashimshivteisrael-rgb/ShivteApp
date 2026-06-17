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
from actividades.models import PictureDayPedido, PictureDayFoto
import zipfile
from io import BytesIO
from django.http import HttpResponse
from actividades.models import ActividadEstado
from django.utils import timezone
from datetime import timedelta
from actividades.models import ShivteGotTalentRol, ShivteGotTalentConcursante, ShivteGotTalentCalificacion
from actividades.models import ShivteTVPedido, ShivteTVVideo
import zipfile
from io import BytesIO
from django.http import HttpResponse
from transporte.models import Camion
from actividades.models import (
    ShevetBankGrupo,
    ShevetBankCuenta,
    ShevetBankGrupoMadrij,
    ShevetBankEstacion,
    ShevetBankMovimiento,
    ShevetBankRonda,
    ShevetBankParticipanteRonda,
    ShevetBankPrestamo,
    ShevetBankSubasta,
    ShevetBankPuja,
    ShevetBankConfig,
)

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

    janijim_disponibles = Janij.objects.filter(kbutza__isnull=True).order_by('nombre')

    if request.method == 'POST':
        kbutza.nombre = request.POST.get('nombre')
        kbutza.cuarto = request.POST.get('cuarto')
        kbutza.save()

        janijim_ids = request.POST.getlist('janijim')

        for janij in Janij.objects.filter(id__in=janijim_ids):
            janij.kbutza = kbutza
            janij.save()

        return redirect(f'/panel-admin/kbutzot/{kbutza.id}/')

    return render(request, 'editar_kbutza.html', {
        'kbutza': kbutza,
        'janijim_disponibles': janijim_disponibles
    })

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

    janijim_disponibles = Janij.objects.filter(kbutza__isnull=True).order_by('nombre')

    if request.method == 'POST':
        janij_id = request.POST.get('janij')

        if janij_id:
            janij = get_object_or_404(Janij, id=janij_id)
            janij.kbutza = kbutza
            janij.save()

        return redirect(f'/panel-admin/kbutzot/{kbutza.id}/')

    return render(request, 'agregar_janij.html', {
        'kbutza': kbutza,
        'janijim_disponibles': janijim_disponibles
    })

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

def janijim_publicos(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    janijim = []
    titulo = "Janijim"

    if usuario_tipo == 'admin':
        janijim = Janij.objects.all().order_by('nombre')
        titulo = "Todos los janijim"

    elif usuario_tipo == 'madrij':
        usuario = UsuarioCamp.objects.filter(id=usuario_id, tipo='madrij').first()
        if usuario:
            asignacion = MadrijKbutza.objects.filter(usuario=usuario).first()
            if asignacion:
                janijim = Janij.objects.filter(kbutza=asignacion.kbutza)
                titulo = f"Janijim de {asignacion.kbutza.nombre}"

    else:
        return redirect('/')

    return render(request, 'janijim.html', {
        'janijim': janijim,
        'titulo': titulo
    })

def detalle_janij_publico(request, janij_id):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo not in ['admin', 'madrij']:
        return redirect('/login/')

    janij = get_object_or_404(Janij, id=janij_id)

    if usuario_tipo == 'madrij':
        usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
        asignacion = MadrijKbutza.objects.filter(usuario=usuario).first()

        if not asignacion or janij.kbutza != asignacion.kbutza:
            return redirect('/janijim/')

    madrijim = MadrijKbutza.objects.filter(kbutza=janij.kbutza)

    return render(request, 'detalle_janij_publico.html', {
        'janij': janij,
        'madrijim': madrijim
    })

def agregar_janij_general(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    if request.method == 'POST':
        Janij.objects.create(
            nombre=request.POST.get('nombre'),
            nombre_mama=request.POST.get('nombre_mama'),
            tel_mama=request.POST.get('tel_mama'),
            nombre_papa=request.POST.get('nombre_papa'),
            tel_papa=request.POST.get('tel_papa'),
            info_medica=request.POST.get('info_medica'),
        )
        return redirect('/janijim/')

    return render(request, 'agregar_janij_general.html')

def editar_janij_general(request, janij_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    janij = get_object_or_404(Janij, id=janij_id)
    kbutzot = Kbutza.objects.all().order_by('nombre')

    if request.method == 'POST':
        janij.nombre = request.POST.get('nombre')
        janij.nombre_mama = request.POST.get('nombre_mama')
        janij.tel_mama = request.POST.get('tel_mama')
        janij.nombre_papa = request.POST.get('nombre_papa')
        janij.tel_papa = request.POST.get('tel_papa')
        janij.info_medica = request.POST.get('info_medica')

        kbutza_id = request.POST.get('kbutza')
        if kbutza_id:
            janij.kbutza = get_object_or_404(Kbutza, id=kbutza_id)
        else:
            janij.kbutza = None

        janij.save()
        return redirect(f'/janijim/{janij.id}/')

    return render(request, 'editar_janij_general.html', {
        'janij': janij,
        'kbutzot': kbutzot
    })


def eliminar_janij_general(request, janij_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    janij = get_object_or_404(Janij, id=janij_id)

    if request.method == 'POST':
        janij.delete()
        return redirect('/janijim/')

    return redirect('/janijim/')

def crear_admin_temporal(request):
    existe = UsuarioCamp.objects.filter(username='admin').first()

    if not existe:
        UsuarioCamp.objects.create(
            nombre='Admin',
            username='admin',
            password='1234',
            tipo='admin'
        )

    return redirect('/login/')

def picture_day_admin(request):
    estado, creado = ActividadEstado.objects.get_or_create(nombre='picture_day')
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    if request.method == 'POST':
        if request.POST.get('tipo_form') == 'estado':
            estado.abierta = request.POST.get('abierta') == 'on'
            estado.save()
            return redirect('/panel-admin/picture-day/')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')

        if titulo:
            kbutzot = Kbutza.objects.all()

            for kbutza in kbutzot:
                PictureDayPedido.objects.create(
                    kbutza=kbutza,
                    titulo=titulo,
                    descripcion=descripcion
                )

        return redirect('/panel-admin/picture-day/')

    pedidos = PictureDayPedido.objects.all().order_by('kbutza__nombre', 'titulo')

    data = []
    for p in pedidos:
        foto = PictureDayFoto.objects.filter(pedido=p).first()

        data.append({
            'pedido': p,
            'foto': foto,
            'subida': foto is not None
        })

    return render(request, 'picture_day_admin.html', {
        'data': data,
        'estado': estado
    })

def eliminar_picture_day_foto(request, foto_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    foto = get_object_or_404(PictureDayFoto, id=foto_id)

    if request.method == 'POST':
        foto.delete()

    return redirect('/panel-admin/picture-day/')

def eliminar_picture_day_pedido(request, pedido_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    pedido = get_object_or_404(PictureDayPedido, id=pedido_id)

    if request.method == 'POST':
        pedido.delete()

    return redirect('/panel-admin/picture-day/')

def descargar_picture_day_zip(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    fotos = PictureDayFoto.objects.all().order_by(
        'pedido__kbutza__nombre',
        'pedido__titulo'
    )

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for foto in fotos:
            if foto.archivo:
                extension = foto.archivo.name.split('.')[-1]

                nombre_kbutza = foto.pedido.kbutza.nombre.replace('/', '-')
                nombre_foto = foto.pedido.titulo.replace('/', '-')

                nombre_carpeta = nombre_foto

                nombre_archivo = f"{nombre_carpeta}/{nombre_kbutza}.{extension}"

                zip_file.writestr(nombre_archivo, foto.archivo.read())

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="picture_day_fotos.zip"'

    return response

def picture_day_madrij(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    asignacion = MadrijKbutza.objects.filter(usuario=usuario).first()

    if not asignacion:
        return render(request, 'picture_day_madrij.html', {
            'sin_kbutza': True
        })

    kbutza = asignacion.kbutza
    pedidos = PictureDayPedido.objects.filter(kbutza=kbutza).order_by('titulo')

    data = []
    for p in pedidos:
        foto = PictureDayFoto.objects.filter(pedido=p).first()
        data.append({
            'pedido': p,
            'foto': foto,
            'subida': foto is not None
        })

    return render(request, 'picture_day_madrij.html', {
        'kbutza': kbutza,
        'data': data
    })


def subir_picture_day(request, pedido_id):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    pedido = get_object_or_404(PictureDayPedido, id=pedido_id)

    asignacion = MadrijKbutza.objects.filter(usuario=usuario, kbutza=pedido.kbutza).first()
    if not asignacion:
        return redirect('/picture-day/')

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if archivo:
            PictureDayFoto.objects.create(
                pedido=pedido,
                archivo=archivo,
                subido_por=usuario
            )

        return redirect('/picture-day/')

    return render(request, 'subir_picture_day.html', {
        'pedido': pedido
    })


def picture_day_publico(request):
    fotos = PictureDayFoto.objects.all().order_by('-fecha_subida')

    return render(request, 'picture_day_publico.html', {
        'fotos': fotos
    })

def picture_day_entrada(request):
    estado, creado = ActividadEstado.objects.get_or_create(nombre='picture_day')

    if not estado.abierta:
        return render(request, 'actividad_cerrada.html', {
            'nombre_actividad': 'Picture Day'
        })

    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo == 'admin':
        return redirect('/panel-admin/picture-day/')
    elif usuario_tipo == 'madrij':
        return redirect('/picture-day/')
    else:
        return redirect('/picture-day-publico/')

def actividades(request):
    usuario_tipo = request.session.get('usuario_tipo')

    return render(request, 'actividades.html', {
        'usuario_tipo': usuario_tipo
    })



def got_talent_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    madrijim = UsuarioCamp.objects.filter(tipo='madrij').order_by('nombre')
    roles = ShivteGotTalentRol.objects.all().order_by('rol', 'usuario__nombre')
    concursantes = ShivteGotTalentConcursante.objects.all().order_by('janij__nombre')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol = request.POST.get('rol')

        if usuario_id and rol:
            usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')

            ShivteGotTalentRol.objects.get_or_create(
                usuario=usuario,
                rol=rol
            )

        return redirect('/panel-admin/got-talent/')

    return render(request, 'got_talent_admin.html', {
        'madrijim': madrijim,
        'roles': roles,
        'concursantes': concursantes
    })

def got_talent_inscripciones(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')

    tiene_permiso = ShivteGotTalentRol.objects.filter(
        usuario=usuario,
        rol='inscripciones'
    ).exists()

    if not tiene_permiso:
        return render(request, 'got_talent_sin_permiso.html')

    janijim = Janij.objects.all().order_by('nombre')
    concursantes = ShivteGotTalentConcursante.objects.all().order_by('janij__nombre')

    if request.method == 'POST':
        janij_id = request.POST.get('janij')
        talento = request.POST.get('talento')

        if janij_id and talento:
            janij = get_object_or_404(Janij, id=janij_id)

            ShivteGotTalentConcursante.objects.get_or_create(
                janij=janij,
                defaults={'talento': talento}
            )

        return redirect('/got-talent/inscripciones/')

    return render(request, 'got_talent_inscripciones.html', {
        'janijim': janijim,
        'concursantes': concursantes
    })

def got_talent_iniciar_concursante(request, concursante_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    concursante = get_object_or_404(ShivteGotTalentConcursante, id=concursante_id)

    if request.method == 'POST':
        ShivteGotTalentConcursante.objects.all().update(activo=False)

        concursante.activo = True
        concursante.terminado = False
        concursante.save()

    return redirect('/panel-admin/got-talent/')


def got_talent_terminar_concursante(request, concursante_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    concursante = get_object_or_404(ShivteGotTalentConcursante, id=concursante_id)

    if request.method == 'POST':
        concursante.activo = False
        concursante.terminado = True
        concursante.save()

    return redirect('/panel-admin/got-talent/')


def got_talent_pantalla(request):
    concursante = ShivteGotTalentConcursante.objects.filter(activo=True).first()

    return render(request, 'got_talent_pantalla.html', {
        'concursante': concursante
    })

def got_talent_juez(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    juez = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')

    es_juez = ShivteGotTalentRol.objects.filter(
        usuario=juez,
        rol='juez'
    ).exists()

    if not es_juez:
        return render(request, 'got_talent_sin_permiso.html')

    concursante = ShivteGotTalentConcursante.objects.filter(activo=True).first()
    calificacion_existente = None

    if concursante:
        calificacion_existente = ShivteGotTalentCalificacion.objects.filter(
            concursante=concursante,
            juez=juez
        ).first()

    if request.method == 'POST' and concursante and not calificacion_existente:
        originalidad = int(request.POST.get('originalidad'))
        ejecucion = int(request.POST.get('ejecucion'))
        general = int(request.POST.get('general'))

        ShivteGotTalentCalificacion.objects.create(
            concursante=concursante,
            juez=juez,
            originalidad=originalidad,
            ejecucion=ejecucion,
            general=general
        )

        return redirect('/got-talent/juez/')

    return render(request, 'got_talent_juez.html', {
        'concursante': concursante,
        'calificacion_existente': calificacion_existente
    })

def got_talent_resultados_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    concursantes = ShivteGotTalentConcursante.objects.all()

    resultados = []

    for c in concursantes:
        calificaciones = ShivteGotTalentCalificacion.objects.filter(concursante=c)

        total = 0
        cantidad_jueces = calificaciones.count()

        for cal in calificaciones:
            total += cal.originalidad + cal.ejecucion + cal.general

        promedio = 0
        if cantidad_jueces > 0:
            promedio = total / cantidad_jueces

        resultados.append({
            'concursante': c,
            'total': total,
            'promedio': promedio,
            'cantidad_jueces': cantidad_jueces
        })

    resultados = sorted(resultados, key=lambda x: x['total'], reverse=True)

    return render(request, 'got_talent_resultados_admin.html', {
        'resultados': resultados
    })

def eliminar_got_talent_concursante(request, concursante_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    concursante = get_object_or_404(
        ShivteGotTalentConcursante,
        id=concursante_id
    )

    if request.method == 'POST':
        concursante.delete()

    return redirect('/panel-admin/got-talent/')

def editar_got_talent_concursante(request, concursante_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    concursante = get_object_or_404(
        ShivteGotTalentConcursante,
        id=concursante_id
    )

    if request.method == 'POST':
        concursante.talento = request.POST.get('talento')
        concursante.save()

        return redirect('/panel-admin/got-talent/')

    return render(
        request,
        'editar_got_talent_concursante.html',
        {
            'concursante': concursante
        }
    )

def shivte_tv_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    kbutzot = Kbutza.objects.all().order_by('nombre')

    if request.method == 'POST':
        kbutza_id = request.POST.get('kbutza')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')

        if kbutza_id and titulo:
            kbutza = get_object_or_404(Kbutza, id=kbutza_id)

            pedido, creado = ShivteTVPedido.objects.get_or_create(
                kbutza=kbutza,
                defaults={
                    'titulo': titulo,
                    'descripcion': descripcion
                }
            )

            if not creado:
                pedido.titulo = titulo
                pedido.descripcion = descripcion
                pedido.save()

        return redirect('/panel-admin/shivte-tv/')

    pedidos = ShivteTVPedido.objects.all().order_by('kbutza__nombre')

    data = []
    for p in pedidos:
        video = ShivteTVVideo.objects.filter(pedido=p).first()
        data.append({
            'pedido': p,
            'video': video,
            'subido': video is not None
        })

    return render(request, 'shivte_tv_admin.html', {
        'kbutzot': kbutzot,
        'data': data
    })


def shivte_tv_madrij(request):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    asignacion = MadrijKbutza.objects.filter(usuario=usuario).first()

    if not asignacion:
        return render(request, 'shivte_tv_madrij.html', {
            'sin_kbutza': True
        })

    pedido = ShivteTVPedido.objects.filter(kbutza=asignacion.kbutza).first()
    video = None

    if pedido:
        video = ShivteTVVideo.objects.filter(pedido=pedido).first()

    return render(request, 'shivte_tv_madrij.html', {
        'kbutza': asignacion.kbutza,
        'pedido': pedido,
        'video': video
    })


def subir_shivte_tv(request, pedido_id):
    usuario_id = request.session.get('usuario_id')
    usuario_tipo = request.session.get('usuario_tipo')

    if usuario_tipo != 'madrij':
        return redirect('/login/')

    usuario = get_object_or_404(UsuarioCamp, id=usuario_id, tipo='madrij')
    pedido = get_object_or_404(ShivteTVPedido, id=pedido_id)

    asignacion = MadrijKbutza.objects.filter(usuario=usuario, kbutza=pedido.kbutza).first()
    if not asignacion:
        return redirect('/shivte-tv/')

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if archivo:
            ShivteTVVideo.objects.update_or_create(
                pedido=pedido,
                defaults={
                    'archivo': archivo,
                    'subido_por': usuario
                }
            )

        return redirect('/shivte-tv/')

    return render(request, 'subir_shivte_tv.html', {
        'pedido': pedido
    })


def shivte_tv_publico(request):
    videos = ShivteTVVideo.objects.all().order_by('pedido__kbutza__nombre')

    return render(request, 'shivte_tv_publico.html', {
        'videos': videos
    })

def descargar_shivte_tv(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

        videos = ShivteTVVideo.objects.select_related(
            'pedido',
            'pedido__kbutza'
        )

        for video in videos:

            ruta = video.archivo.path

            extension = ruta.split('.')[-1]

            nombre_archivo = (
                f"{video.pedido.kbutza.nombre}"
                f" - "
                f"{video.pedido.titulo}"
                f".{extension}"
            )

            zip_file.write(
                ruta,
                arcname=nombre_archivo
            )

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/zip'
    )

    response['Content-Disposition'] = (
        'attachment; filename="ShivteTV.zip"'
    )

    return response

def shevet_bank_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    grupos = ShevetBankGrupo.objects.all()
    madrijim = UsuarioCamp.objects.filter(tipo='madrij')
    janijim = Janij.objects.all()
    estaciones = ShevetBankEstacion.objects.all()
    cuentas = ShevetBankCuenta.objects.all().order_by('janij__nombre')

    config, creado = ShevetBankConfig.objects.get_or_create(id=1)

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        # crear grupo
        if tipo == 'grupo':
            nombre = request.POST.get('nombre')

            if nombre:
                ShevetBankGrupo.objects.create(
                    nombre=nombre
                )

        # asignar madrij
        elif tipo == 'madrij':
            grupo_id = request.POST.get('grupo')
            madrij_id = request.POST.get('madrij')

            ShevetBankGrupoMadrij.objects.create(
                grupo_id=grupo_id,
                madrij_id=madrij_id
            )

        # crear tarjeta janij
        elif tipo == 'tarjeta':
            grupo_id = request.POST.get('grupo')
            janij_id = request.POST.get('janij')
            tarjeta = request.POST.get('tarjeta')

            ShevetBankCuenta.objects.create(
                grupo_id=grupo_id,
                janij_id=janij_id,
                numero_tarjeta=tarjeta,
                saldo=0
            )
        
        # crear estacion
        elif tipo == 'estacion':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio = request.POST.get('precio')
            encargado_id = request.POST.get('encargado')
            es_banco = request.POST.get('es_banco') == 'on'

            ShevetBankEstacion.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=int(precio or 0),
                encargado_id=encargado_id,
                es_banco=es_banco
            )

        elif tipo == "finalizar":

            config.actividad_activa = False
            config.grupos_revelados = True
            config.save()

        return redirect('/panel-admin/shevet-bank/')

    return render(request, 'shevet_bank_admin.html', {
        'grupos': grupos,
        'madrijim': madrijim,
        'janijim': janijim,
        'estaciones': estaciones,
        'config': config,
        'cuentas': cuentas,
    })

def shevet_bank_madrij(request):
    usuario_id = request.session.get('usuario_id')

    usuario = get_object_or_404(
        UsuarioCamp,
        id=usuario_id,
        tipo='madrij'
    )

    estacion = ShevetBankEstacion.objects.filter(
        encargado=usuario
    ).first()

    if not estacion:
        return render(request, 'shevet_bank_madrij.html', {
            'sin_estacion': True
        })
    
        # SI ES BANCO
    if estacion.es_banco:
        mensaje = None
        cuenta = None
        prestamo_abierto = None

        tarjeta = request.POST.get('tarjeta') or request.GET.get('tarjeta')

        if tarjeta:
            cuenta = ShevetBankCuenta.objects.filter(numero_tarjeta=tarjeta).first()
 
            if cuenta:
                prestamo_abierto = ShevetBankPrestamo.objects.filter(
                    cuenta=cuenta,
                    abierto=True
                ).first()
            else:
                mensaje = "Tarjeta no encontrada"

        if request.method == 'POST':
            accion = request.POST.get('accion')
            cantidad = int(request.POST.get('cantidad') or 0)

            if cuenta and accion == "meter":
                cuenta.saldo += cantidad
                cuenta.save()
                ShevetBankMovimiento.objects.create(
                    cuenta=cuenta,
                    estacion=estacion,
                    madrij=usuario,
                    cantidad=cantidad,
                    nota="Banco: meter dinero"
                )
                mensaje = "Dinero agregado"

            elif cuenta and accion == "sacar":
                if cuenta.saldo >= cantidad:
                    cuenta.saldo -= cantidad
                    cuenta.save()
                    ShevetBankMovimiento.objects.create(
                        cuenta=cuenta,
                        estacion=estacion,
                        madrij=usuario,
                        cantidad=-cantidad,
                        nota="Banco: sacar dinero"
                    )
                    mensaje = "Dinero retirado"
                else:
                    mensaje = "Saldo insuficiente"

            elif cuenta and accion == "prestamo":
                cuenta.saldo += cantidad
                cuenta.save()

                ShevetBankPrestamo.objects.create(
                    cuenta=cuenta,
                    banco=estacion,
                    encargado=usuario,
                    cantidad=cantidad,
                    abierto=True
                )
                ShevetBankMovimiento.objects.create(
                    cuenta=cuenta,
                    estacion=estacion,
                    madrij=usuario,
                    cantidad=cantidad,
                    nota="Préstamo creado"
                )

                mensaje = "Préstamo creado"

            elif cuenta and accion == "pagar_prestamo":
                if prestamo_abierto and cuenta.saldo >= prestamo_abierto.cantidad:
                    cuenta.saldo -= prestamo_abierto.cantidad
                    cuenta.save()

                    ShevetBankMovimiento.objects.create(
                        cuenta=cuenta,
                        estacion=estacion,
                        madrij=usuario,
                        cantidad=-prestamo_abierto.cantidad,
                        nota="Préstamo pagado"
                    )

                    prestamo_abierto.abierto = False
                    prestamo_abierto.fecha_cierre = timezone.now()
                    prestamo_abierto.save()

                    mensaje = "Préstamo pagado"
                else:
                    mensaje = "No se pudo pagar el préstamo"

            elif cuenta and accion == "cobrar_doble":
                if prestamo_abierto:
                    total = prestamo_abierto.cantidad * 2
                    cuenta.saldo = max(0, cuenta.saldo - total)
                    cuenta.save()

                    ShevetBankMovimiento.objects.create(
                        cuenta=cuenta,
                        estacion=estacion,
                        madrij=usuario,
                        cantidad=-total,
                        nota="Préstamo cobrado doble"
                    )

                    prestamo_abierto.abierto = False
                    prestamo_abierto.cobrado_doble = True
                    prestamo_abierto.fecha_cierre = timezone.now()
                    prestamo_abierto.save()

                    mensaje = "Préstamo cobrado doble"
                else:
                    mensaje = "No hay préstamo abierto"

        return render(request, 'shevet_bank_banco.html', {
            'estacion': estacion,
            'mensaje': mensaje,
            'cuenta': cuenta,
            'prestamo_abierto': prestamo_abierto,
            'tarjeta': tarjeta
        })


    ronda = ShevetBankRonda.objects.filter(
        estacion=estacion,
        activa=True
    ).first()


    mensaje = None


    # crear ronda nueva
    if request.method == 'POST':

        accion = request.POST.get('accion')


        if accion == 'crear':
            ronda = ShevetBankRonda.objects.create(
                estacion=estacion,
                bote=0,
                activa=True
            )


        elif accion == 'agregar':

            tarjeta = request.POST.get('tarjeta')

            cuenta = ShevetBankCuenta.objects.filter(
                numero_tarjeta=tarjeta
            ).first()

            if not cuenta:
                mensaje = "Tarjeta no existe"

            elif cuenta.saldo < estacion.precio:
                mensaje = "Saldo insuficiente"

            else:
                cuenta.saldo -= estacion.precio
                cuenta.save()

                ronda.bote += estacion.precio
                ronda.save()

                ShevetBankParticipanteRonda.objects.create(
                    ronda=ronda,
                    cuenta=cuenta
                )

                mensaje = "Jugador agregado"


        elif accion == 'finalizar':

            ganador_id = request.POST.get('ganador')

            ganador = ShevetBankCuenta.objects.get(
                id=ganador_id
            )

            ganador.saldo += ronda.bote
            ganador.save()

            ronda.activa = False
            ronda.ganador = ganador
            ronda.save()

            mensaje = "Ronda terminada"


    participantes = []

    if ronda:
        participantes = ShevetBankParticipanteRonda.objects.filter(
            ronda=ronda
        )


    return render(request,'shevet_bank_madrij.html',{
        'estacion': estacion,
        'ronda': ronda,
        'participantes': participantes,
        'mensaje': mensaje
    })

def shevet_bank_historial_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    movimientos = ShevetBankMovimiento.objects.all().order_by('-fecha')
    rondas = ShevetBankRonda.objects.all().order_by('-fecha_inicio')
    prestamos = ShevetBankPrestamo.objects.all().order_by('-fecha_inicio')

    return render(request, 'shevet_bank_historial_admin.html', {
        'movimientos': movimientos,
        'rondas': rondas,
        'prestamos': prestamos
    })

def eliminar_shevet_grupo(request, grupo_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    grupo = get_object_or_404(ShevetBankGrupo, id=grupo_id)

    if request.method == 'POST':
        grupo.delete()

    return redirect('/panel-admin/shevet-bank/')


def eliminar_shevet_cuenta(request, cuenta_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    cuenta = get_object_or_404(ShevetBankCuenta, id=cuenta_id)

    if request.method == 'POST':
        cuenta.delete()

    return redirect('/panel-admin/shevet-bank/')


def eliminar_shevet_estacion(request, estacion_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    estacion = get_object_or_404(ShevetBankEstacion, id=estacion_id)

    if request.method == 'POST':
        estacion.delete()

    return redirect('/panel-admin/shevet-bank/')


def shevet_bank_saldos_admin(request):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    cuentas = ShevetBankCuenta.objects.all().order_by('janij__nombre')

    return render(request, 'shevet_bank_saldos_admin.html', {
        'cuentas': cuentas
    })  

def editar_shevet_grupo(request, grupo_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    grupo = get_object_or_404(ShevetBankGrupo, id=grupo_id)

    if request.method == 'POST':
        grupo.nombre = request.POST.get('nombre')
        grupo.save()
        return redirect('/panel-admin/shevet-bank/')

    return render(request, 'editar_shevet_grupo.html', {
        'grupo': grupo
    })

def editar_shevet_cuenta(request, cuenta_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    cuenta = get_object_or_404(ShevetBankCuenta, id=cuenta_id)
    grupos = ShevetBankGrupo.objects.all()
    janijim = Janij.objects.all()

    if request.method == 'POST':
        cuenta.numero_tarjeta = request.POST.get('tarjeta')
        cuenta.saldo = int(request.POST.get('saldo') or 0)
        cuenta.grupo_id = request.POST.get('grupo')
        cuenta.janij_id = request.POST.get('janij')
        cuenta.save()

        return redirect('/panel-admin/shevet-bank/saldos/')

    return render(request, 'editar_shevet_cuenta.html', {
        'cuenta': cuenta,
        'grupos': grupos,
        'janijim': janijim
    })

def editar_shevet_estacion(request, estacion_id):
    if request.session.get('usuario_tipo') != 'admin':
        return redirect('/login/')

    estacion = get_object_or_404(ShevetBankEstacion, id=estacion_id)
    madrijim = UsuarioCamp.objects.filter(tipo='madrij')

    if request.method == 'POST':
        estacion.nombre = request.POST.get('nombre')
        estacion.descripcion = request.POST.get('descripcion')
        estacion.precio = int(request.POST.get('precio') or 0)
        estacion.encargado_id = request.POST.get('encargado')
        estacion.es_banco = request.POST.get('es_banco') == 'on'
        estacion.save()

        return redirect('/panel-admin/shevet-bank/')

    return render(request, 'editar_shevet_estacion.html', {
        'estacion': estacion,
        'madrijim': madrijim
    })