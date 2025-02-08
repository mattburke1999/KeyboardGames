from app.data_access.db import BaseDB
import psycopg2 as pg

from app.games.data_access.models import Game_Info
from app.games.data_access.models import Score_View

class GameDB(BaseDB):
    def get_games(self) -> dict[str, Game_Info]:
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, title, title_style, title_color, bg_rot, bg_color1, bg_color2, abbrev_name, duration, basic_circle_template from games order by id')
                results = cur.fetchall()
                return {res[7]: Game_Info(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[8], res[9]) for res in results} if results else {}

    def update_score(self, conn: pg.extensions.connection, user_id: int, game_id: int, score: int) -> Score_View | None:
        with conn.cursor() as cur:
            cur.execute('select high_scores, points_added, score_rank from update_scores(%s, %s, %s)', (user_id, game_id, score))
            result = cur.fetchone()
            return Score_View(*result) if result else None
  