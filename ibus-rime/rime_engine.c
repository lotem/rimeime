#include <string.h>
#include <rime_api.h>
#include "rime_engine.h"

typedef struct _IBusRimeEngine IBusRimeEngine;
typedef struct _IBusRimeEngineClass IBusRimeEngineClass;

struct _IBusRimeEngine {
  IBusEngine parent;

  /* members */
  RimeSessionId session_id;
  IBusLookupTable *table;
};

struct _IBusRimeEngineClass {
  IBusEngineClass parent;
};

/* functions prototype */
static void	ibus_rime_engine_class_init	(IBusRimeEngineClass	*klass);
static void	ibus_rime_engine_init		(IBusRimeEngine		*engine);
static void	ibus_rime_engine_destroy		(IBusRimeEngine		*engine);
static gboolean 
ibus_rime_engine_process_key_event
(IBusEngine             *engine,
 guint               	 keyval,
 guint               	 keycode,
 guint               	 modifiers);
static void ibus_rime_engine_focus_in    (IBusEngine             *engine);
static void ibus_rime_engine_focus_out   (IBusEngine             *engine);
static void ibus_rime_engine_reset       (IBusEngine             *engine);
static void ibus_rime_engine_enable      (IBusEngine             *engine);
static void ibus_rime_engine_disable     (IBusEngine             *engine);
static void ibus_engine_set_cursor_location (IBusEngine             *engine,
                                             gint                    x,
                                             gint                    y,
                                             gint                    w,
                                             gint                    h);
static void ibus_rime_engine_set_capabilities
(IBusEngine             *engine,
 guint                   caps);
static void ibus_rime_engine_page_up     (IBusEngine             *engine);
static void ibus_rime_engine_page_down   (IBusEngine             *engine);
static void ibus_rime_engine_cursor_up   (IBusEngine             *engine);
static void ibus_rime_engine_cursor_down (IBusEngine             *engine);
static void ibus_rime_property_activate  (IBusEngine             *engine,
                                          const gchar            *prop_name,
                                          gint                    prop_state);
static void ibus_rime_engine_property_show
(IBusEngine             *engine,
 const gchar            *prop_name);
static void ibus_rime_engine_property_hide
(IBusEngine             *engine,
 const gchar            *prop_name);

static void ibus_rime_engine_update      (IBusRimeEngine      *rime);

G_DEFINE_TYPE (IBusRimeEngine, ibus_rime_engine, IBUS_TYPE_ENGINE)

static void
ibus_rime_engine_class_init (IBusRimeEngineClass *klass)
{
  IBusObjectClass *ibus_object_class = IBUS_OBJECT_CLASS (klass);
  IBusEngineClass *engine_class = IBUS_ENGINE_CLASS (klass);
	
  ibus_object_class->destroy = (IBusObjectDestroyFunc) ibus_rime_engine_destroy;

  engine_class->process_key_event = ibus_rime_engine_process_key_event;
}

static void
ibus_rime_engine_init (IBusRimeEngine *rime)
{
  rime->session_id = RimeCreateSession();

  rime->table = ibus_lookup_table_new(9, 0, TRUE, FALSE);
  g_object_ref_sink(rime->table);
}

static void
ibus_rime_engine_destroy (IBusRimeEngine *rime)
{
  if (rime->session_id) {
    RimeDestroySession(rime->session_id);
    rime->session_id = 0;
  }

  if (rime->table) {
    g_object_unref(rime->table);
    rime->table = NULL;
  }

  ((IBusObjectClass *) ibus_rime_engine_parent_class)->destroy((IBusObject *)rime);
}

static void ibus_rime_engine_update(IBusRimeEngine *rime)
{
  const int GLOW = 0xffffff;
  const int DARK = 0x606060;
  const int BLACK = 0x000000;
  const int LUNA = 0xffff7f;
  const int SHADOW = 0xd4d4d4;
  const int HIGHLIGHT = 0x0a3dfa;

  RimeCommit commit = {0};
  if (RimeGetCommit(rime->session_id, &commit)) {
    IBusText *text;
    text = ibus_text_new_from_string(commit.text);
    ibus_engine_commit_text((IBusEngine *)rime, text);  // the text object will be released by ibus
    RimeFreeCommit(&commit);
  }
  
  RimeContext context = {0};
  RIME_STRUCT_INIT(RimeContext, context);
  if (!RimeGetContext(rime->session_id, &context) ||
      context.composition.length == 0) {
    ibus_engine_hide_auxiliary_text((IBusEngine *)rime);
    ibus_engine_hide_lookup_table((IBusEngine *)rime);
    RimeFreeContext(&context);
    return;
  }

  // begin updating UI

  IBusText *text = ibus_text_new_from_string(context.composition.preedit);
  glong preedit_len = g_utf8_strlen(context.composition.preedit, -1);
  glong cursor_pos = g_utf8_strlen(context.composition.preedit, context.composition.cursor_pos);
  text->attrs = ibus_attr_list_new();
  //ibus_attr_list_append(text->attrs,
  //                      ibus_attr_underline_new(IBUS_ATTR_UNDERLINE_SINGLE, 0, cursor_pos));
  if (context.composition.sel_start < context.composition.sel_end) {
    glong start = g_utf8_strlen(context.composition.preedit, context.composition.sel_start);
    glong end = g_utf8_strlen(context.composition.preedit, context.composition.sel_end);
    ibus_attr_list_append(text->attrs,
                          ibus_attr_foreground_new(BLACK, start, end));
    ibus_attr_list_append(text->attrs,
                          ibus_attr_background_new(SHADOW, start, end));
  }
  ibus_engine_update_auxiliary_text((IBusEngine *)rime,
                                    text,
                                    TRUE);

  ibus_lookup_table_clear(rime->table);
  if (context.menu.num_candidates) {
    int i;
    int num_select_keys = strlen(context.menu.select_keys);
    for (i = 0; i < context.menu.num_candidates; ++i) {
      gchar* text = context.menu.candidates[i].text;
      gchar* comment = context.menu.candidates[i].comment;
      IBusText *cand_text = NULL;
      if (comment) {
        gchar* temp = g_strconcat(text, " ", comment, NULL);
        cand_text = ibus_text_new_from_string(temp);
        g_free(temp);
        int text_len = g_utf8_strlen(text, -1);
        int end_index = ibus_text_get_length(cand_text);
        ibus_text_append_attribute(cand_text,
                                   IBUS_ATTR_TYPE_FOREGROUND,
                                   DARK,
                                   text_len, end_index);
      }
      else {
        cand_text = ibus_text_new_from_string(text);
      }
      ibus_lookup_table_append_candidate(rime->table, cand_text);
      IBusText *label = NULL;
      if (i < num_select_keys) {
        label = ibus_text_new_from_unichar(context.menu.select_keys[i]);
      }
      else {
        label = ibus_text_new_from_printf("%d", (i + 1) % 10);
      }
      ibus_lookup_table_set_label(rime->table, i, label);
    }
    ibus_lookup_table_set_cursor_pos(rime->table, context.menu.highlighted_candidate_index);
    ibus_engine_update_lookup_table((IBusEngine *)rime, rime->table, TRUE);
  }
  else {
    ibus_engine_hide_lookup_table((IBusEngine *)rime);
  }

   // end updating UI
  
  RimeFreeContext(&context);
}

static gboolean 
ibus_rime_engine_process_key_event (IBusEngine *engine,
                                    guint       keyval,
                                    guint       keycode,
                                    guint       modifiers)
{
  IBusRimeEngine *rime = (IBusRimeEngine *)engine;

  modifiers &= (IBUS_RELEASE_MASK | IBUS_CONTROL_MASK | IBUS_MOD1_MASK);

  if (!RimeFindSession(rime->session_id)) {
    rime->session_id = RimeCreateSession();
  }
  if (!rime->session_id) {  // service disabled
    return FALSE;
  }
  gboolean result = RimeProcessKey(rime->session_id, keyval, modifiers);
  ibus_rime_engine_update(rime);
  return result;
}
