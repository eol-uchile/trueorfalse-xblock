function TrueOrFalseEditBlock(runtime, element) {
    console.log("hola");
    $(element).find('.save-button').bind('click', function(eventObject) {
      eventObject.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

      // Generate a list of questions
      var questions_list = [];
      $.each( $(element).find('input[name=question]'), function( key, value ) {
        question  = $(this).val();
        id_question = $(this).attr('question-id');
        answer = $('[answer-id='+id_question+']').val();
        questions_list.push({
          'id_question': id_question,
          'question': question,
          'answer':answer
        });
      });
      var data = {
        display_name: $(element).find('input[name=display_name]').val(),
        weight: $(element).find('input[name=weight]').val(),
        max_attempts: $(element).find('input[name=max_attempts]').val(),
        show_answer: $(element).find('select.show_answer').val(),
        questions_list: questions_list
      };
      if ($.isFunction(runtime.notify)) {
        runtime.notify('save', {state: 'start'});
      }
      $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
        if ($.isFunction(runtime.notify)) {
          runtime.notify('save', {state: 'end'});
        }
      });
    });
  
    $(element).find('.cancel-button').bind('click', function(eventObject) {
      eventObject.preventDefault();
      runtime.notify('cancel', {});
    });

    $(element).find('.add-button').bind('click', function(eventObject) {
      eventObject.preventDefault();
      var max_id = 0;
      $.each( $(element).find('input[name=question]'), function( key, value ) {
        cur_id = parseInt($(this).attr('question-id'));
        if(max_id < cur_id)
          max_id = cur_id;
      });
      var new_id = max_id + 1;
      var new_question = `
      <div class="border-question div-question-${new_id}">
        <div class="wrapper-comp-setting">
          <label class="label setting-label" for="question">Pregunta</label>
          <input class="input setting-input" name="question" question-id="${new_id}" value="Nueva Pregunta" type="text" />
        </div>
        <div class="wrapper-comp-setting">
          <label class="label setting-label" for="answer">Respuesta</label>
          <select name="answer" answer-id="${new_id}">
            <option value="V" selected>Verdadero</option>
            <option value="F">Falso</option>
          </select>
        </div>
        <div class="setting-button">
          <button remove-id="${new_id}" class="question-button remove-button">Eliminar Pregunta</a>
        </div>
      </div>
      `;
      $(element).find("#questions_list").append(new_question);
      remove_question_button();
    });

    function remove_question_button(){
      $(element).find('.remove-button').bind('click', function(eventObject) {
        eventObject.preventDefault();
        var remove_id = $(this).attr('remove-id');
        $(element).find(".div-question-"+remove_id ).remove();
      });
    }
    remove_question_button();

}