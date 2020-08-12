function TrueOrFalseXBlock(runtime, element, settings) {

    
    var $ = window.jQuery;
    var $element = $(element);
    var buttonCheck = $element.find('.check');
    var buttonVerRespuesta = $element.find('.ver_respuesta');
    var botonesVoF = $element.find('.opcion');
    var lasRespuestas = $element.find('.lasrespuestas');
    var subFeedback = $element.find('.submission-feedback');
    var statusDiv = $element.find('.status');
    var problem_progress = $element.find('.problem-progress');

    function updateText(result) {
        //reviso si estoy mostrando correctitud
        if(result.show_correctness != 'never'){
            //actualizo el texto de correcto o incorrecto
            if(result.score >= 1){
                $element.find('.notificacion').html('');
                $element.find('.notificacion').removeClass('lineaarriba');
                $element.find('.notificacion').removeClass('incorrecto');
                $element.find('.notificacion').removeClass('dontshowcorrectness');
                $element.find('.notificacion').removeClass('parcial');
                $element.find('.notificacion').addClass('correcto');
                $element.find('.notificacion.correcto').addClass('lineaarriba');
                $element.find('.notificacion.correcto').html('<img src="'+settings.image_path+'correct-icon.png"/>'+result.texto);
                $element.find('.elticket').html('<img src="'+settings.image_path+'correct-icon.png"/>');
            }
            else{
                $element.find('.notificacion').html('');
                $element.find('.notificacion').removeClass('lineaarriba');
                $element.find('.notificacion').removeClass('correcto');
                $element.find('.notificacion').removeClass('dontshowcorrectness');
                $element.find('.notificacion').removeClass('parcial');
                $element.find('.notificacion').addClass('incorrecto');
                $element.find('.notificacion.incorrecto').addClass('lineaarriba');
                if(result.score > 0){
                    $element.find('.notificacion.incorrecto').addClass('parcial');
                    $element.find('.notificacion.incorrecto').html('<img src="'+settings.image_path+'partial-icon.png"/>'+result.texto);
                    $element.find('.elticket').html('<img src="'+settings.image_path+'partial-icon.png"/>');
                }
                else{
                    $element.find('.notificacion.incorrecto').html('<img src="'+settings.image_path+'incorrect-icon.png"/>'+result.texto);
                    $element.find('.elticket').html('<img src="'+settings.image_path+'incorrect-icon.png"/>');
                }
            }

            statusDiv.removeClass('correct');
            statusDiv.removeClass('incorrect');
            statusDiv.removeClass('unanswered');
            statusDiv.addClass(result.indicator_class);
            problem_progress.text(result.problem_progress);
        }
        else{
            statusDiv.removeClass('correct');
            statusDiv.removeClass('incorrect');
            statusDiv.removeClass('unanswered');
            //no deberia pasar pero por si las moscas
            if(result.indicator_class == 'unanswered')
                statusDiv.addClass('unanswered');
            $element.find('.notificacion').html('');
            $element.find('.notificacion').removeClass('lineaarriba');
            $element.find('.notificacion').removeClass('correcto');
            $element.find('.notificacion').removeClass('incorrecto');
            $element.find('.notificacion').removeClass('parcial');
            $element.find('.notificacion').addClass('dontshowcorrectness');
            $element.find('.notificacion.dontshowcorrectness').addClass('lineaarriba');
            $element.find('.notificacion.dontshowcorrectness').html('<span class="icon fa fa-info-circle" aria-hidden="true"></span>Respuesta enviada.');
            $element.find('.elticket').html();
        }

        //desactivo el boton si es que se supero el nro de intentos
        var finalice = false;
        if(result.nro_de_intentos > 0){
            subFeedback.text('Has realizado '+result.intentos+' de '+result.nro_de_intentos+' intentos');
            if(result.intentos >= result.nro_de_intentos){
                buttonCheck.attr("disabled", true);
                $element.find('.tablagrande').addClass('noclick');
                finalice = true;
            }
            else{
                buttonCheck.attr("disabled", false);
                $element.find('.tablagrande').removeClass('noclick');
            }
        }
        else{
            buttonCheck.attr("disabled", false);
            $element.find('.tablagrande').removeClass('noclick');
        }

        if(finalice || (result.intentos >0 && result.nro_de_intentos <= 0)){
            if(result.show_answers == 'Finalizado' && !$element.find('.ver_respuesta').length && result.show_correctness != 'never'){
                var mostrar_resp = '<button class="ver_respuesta" data-checking="Cargando..." data-value="Ver Respuesta">'
                                    + '<span class="icon fa fa-info-circle" aria-hidden="true"></span></br>'
                                    + '<span>Mostrar<br/>Respuesta</span>'
                                    + '</button>';
                $element.find('.action').append(mostrar_resp);
            }
            clickVerRespuesta();
        }

        buttonCheck.html("<span>" + buttonCheck[0].dataset.value + "</span>");
    }

    function showAnswers(result){
        $.each( result.preguntas, function( key, value ) {
            $element.find('.opcV'+key).removeClass('correct incorrect');
            $element.find('.opcF'+key).removeClass('correct incorrect');
            if(value.answer){
                if ($element.find('.opcV'+key).hasClass('selv')) {
                    // correct
                    $element.find('.opcV'+key).addClass('correct');
                    $element.find('.opcV'+key).html('&#x2713;')

                } else {
                    // incorrect
                    $element.find('.opcF'+key).addClass('incorrect');
                    $element.find('.opcF'+key).html('&#x2715;')
                }
            }
            else{
                if ($element.find('.opcF'+key).hasClass('self')) {
                    // correct
                    $element.find('.opcF'+key).addClass('correct');
                    $element.find('.opcF'+key).html('&#x2713;')

                } else {
                    // incorrect
                    $element.find('.opcV'+key).addClass('incorrect');
                    $element.find('.opcV'+key).html('&#x2715;')
                }
            }
          });
    }

    var handlerUrl = runtime.handlerUrl(element, 'responder');
    var handlerUrlVerResp = runtime.handlerUrl(element, 'mostrar_respuesta');

    botonesVoF.click(function(eventObject) {
        eventObject.preventDefault();
        var pid = $(this).children("input[type=radio]").attr('pregunta-id');
        $(this).children("input[type=radio]").prop('checked', true);
        $(this).removeClass('correct');
        $(this).removeClass('incorrect');
        if($(this).hasClass('opcV')){
            $(this).addClass('selv');
            $element.find('.opcF'+pid).removeClass('self');
        }
        else{
            $(this).addClass('self');
            $element.find('.opcV'+pid).removeClass('selv');
        }

        // enable submit if all questions are answered
        answers_quantity = $element.find('.radiovof:checked').length;
        question_quantity = $element.find('.opcV').length;
        if(statusDiv.hasClass("unanswered") && answers_quantity === question_quantity && !settings.is_past_due){
            buttonCheck.attr("disabled", false);
        }
    });

    buttonCheck.click(function(eventObject) {
        eventObject.preventDefault();
        buttonCheck.html("<span>" + buttonCheck[0].dataset.checking + "</span>");
        buttonCheck.attr("disabled", true);
        if ($.isFunction(runtime.notify)) {
            runtime.notify('submit', {
                message: 'Submitting...',
                state: 'start'
            });
        }
        var resp,resps = [];
        $element.find('.radiovof:checked').each(function() { // run through each of the checkboxes
            resp = {
              name: $(this).attr('pregunta-id'),
              value: $(this).val()
            };
            resps.push(resp);
          });
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"answers": resps}),
            success: updateText
        });
        if ($.isFunction(runtime.notify)) {
            runtime.notify('submit', {
                state: 'end'
            });
        }
    });


    function clickVerRespuesta(){
        buttonVerRespuesta = $element.find('.ver_respuesta');
        buttonVerRespuesta.click(function(eventObject) {
            eventObject.preventDefault();
            //buttonVerRespuesta.attr("disabled", true);
            $.ajax({
                type: "POST",
                url: handlerUrlVerResp,
                data: JSON.stringify({}),
                success: showAnswers
            });
        });
    }
    clickVerRespuesta();

    lasRespuestas.each(function() {
        if($( this ).val() == 'verdadero'){
            var pid = $( this ).attr('respuesta-id');
            $element.find('.opcV'+pid).click();
        }
        else{
            var pid = $( this ).attr('respuesta-id');
            $element.find('.opcF'+pid).click();
        }
      });

}
