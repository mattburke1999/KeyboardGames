use sqlx::PgPool;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use crate::state::MetadataValue;

pub async fn load_game_metadata(
    pool: &PgPool,
    game_metadata: Arc<Mutex<HashMap<String, HashMap<String, MetadataValue>>>>,
) -> Result<(), sqlx::Error> {
    let rows = sqlx::query!("SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games order by id")
        .fetch_all(pool)
        .await?;
    
    let mut metadata_map = game_metadata.lock().unwrap();
    for row in rows {
        let abbrev_name: Option<String> = Some(row.abbrev_name.clone());
        if abbrev_name.is_some() {
            metadata_map.insert(
                abbrev_name.unwrap(),
                HashMap::from([
                    ("id".to_string(), MetadataValue::Text(row.id.to_string())),
                    ("title".to_string(), MetadataValue::Text(row.title.clone())),
                    ("title_style".to_string(), MetadataValue::Text(row.title_style.clone())),
                    ("title_color".to_string(), MetadataValue::Text(row.title_color.clone())),
                    ("bg_rot".to_string(), MetadataValue::Text(row.bg_rot.to_string())),
                    ("bg_color1".to_string(), MetadataValue::Text(row.bg_color1.clone())),
                    ("bg_color2".to_string(), MetadataValue::Text(row.bg_color2.clone())),
                    ("duration".to_string(), MetadataValue::Text(row.duration.to_string())),
                    (
                        "basic_circle_template".to_string(),
                        MetadataValue::Flag(row.basic_circle_template),
                    ),
                ]),
            );
        }
    }

    Ok(())
}