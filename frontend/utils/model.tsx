import produce, { Draft } from 'immer';

export interface HuntConfig {
  domain: string;
  auto_assign_puzzles_to_meta: boolean;
  discord_server_id: number;
}

export interface SocialAccount {
  provider: string;
  uid: string;
  extra_data: {
    id?: string;
    username?: string;
    discriminator?: string;
    avatar?: string;
    flags?: number;
    public_flags?: number;
    locale?: string;
    mfa_enabled?: boolean;
  };
}

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  socialaccounts: SocialAccount[];
}

export interface Entity {
  slug: string;
  name: string;
  link: string; // link to puzzle relative to hunt domain root
  created: string; // timestamp
  created_by: number; // User.id
  modified: string; // timestamp
  modified_by: number; // User.id
  hidden: boolean; // should ignore this and all references to this if hidden
  tags: {[key: string]: string}; // key value pairs
  notes: string;

  discord_text_channel_id: number;
  discord_voice_channel_id: number;
  sheet_link: string; // full link
}

export interface Round extends Entity {
  auto_assign_puzzles_to_meta: boolean;

  puzzles: string[]; // puzzle slugs
}

export interface Puzzle extends Entity {
  solved: string; // timestamp
  solved_by: number; // User.id
  is_meta: boolean;

  answer: string;
  status: string;
  rounds: string[]; // round slugs
  metas: string[]; // meta slugs
  feeders: string[]; // feeder puzzle slugs
}

export interface Users {
  [id: number]: User;
}
export interface Rounds {
  [slug: string]: Round;
}
export interface Puzzles {
  [slug: string]: Puzzle;
}

export interface Data {
  hunt: HuntConfig;
  users: Users;
  rounds: Rounds;
  round_order: string[];
  puzzles: Puzzles;
  uid?: number;
}

export interface DataUpdate {
  prev_version: number;
  version: number;
  reception_timestamp: number;
  data: any;
  roots: any;
}

export const dataReducer = (state : Data, {ws, cacheRef, update} : {ws, cacheRef, update: DataUpdate}) : Data => {
  return produce(state, (draft : Draft<Data>) => {
    update.reception_timestamp = Date.now();
    if (cacheRef.current === null) {
      cacheRef.current = {
        version: null,
        reception_timestamp: null,
        deltas: {},
      };
    }
    if (update.prev_version === null || cacheRef.current.version === update.prev_version) {
      // apply update
      dataMerge(draft, update.data, update.roots);
      cacheRef.current.version = update.version;
      cacheRef.current.reception_timestamp = Date.now();
      // look through cached updates
      while (cacheRef.current.deltas[cacheRef.current.version]?.version > cacheRef.current.version) {
        const delta = cacheRef.current.deltas[cacheRef.current.version];
        dataMerge(draft, delta.data, delta.roots);
        cacheRef.current.version = delta.version;
      }
      Object.keys(cacheRef.current.deltas).filter(version => Number(version) <= cacheRef.current.version).forEach(version => delete cacheRef.current.deltas[version]);
    } else if (cacheRef.current.version === null || cacheRef.current.version < update.prev_version) {
      // add to cache of updates
      cacheRef.current.deltas[update.prev_version] = update;
      setTimeout(() => {
        if (cacheRef.current.version < update.prev_version) {
          ws.send(JSON.stringify({
            version: cacheRef.current.version,
            force_fetch: true,
          }));
        }
      }, 3000);
    }
  });
};

const _MERGED = {};
const dataMerge = (draft, data, roots) => {
  if (roots === true) return data;
  for (const key in roots) {
    const newData = dataMerge(draft[key], data[key], roots[key]);
    if (newData === undefined) {
      delete draft[key];
    } else if (newData !== _MERGED){
      draft[key] = newData;
    }
  }
  return _MERGED;
};

export const discordLink = (server_id: number, channel_id?: number) => `https://discord.com/channels/${server_id}/${channel_id === null || channel_id === undefined ? '' : channel_id}`;