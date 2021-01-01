import mountElement from 'utils/mount';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
} from 'react';

import * as JSONbig from 'json-bigint';
import { useLocalStorage } from '@rehooks/local-storage';
import SplitPane from 'react-split-pane';

import Base from 'components/base';
import { useLocalStorageObject } from 'components/context';
import Master from 'components/master';
import MasterInfo from 'components/master-info';
import Puzzles from 'components/puzzle';
import PuzzleInfo from 'components/puzzle-info';
import TabBar from 'components/tabbar';
import {
  DiscordFrame,
  ShowIf,
} from 'components/frames';
import baseColors, { statuses as baseStatuses } from 'utils/colors';
import * as Model from 'utils/model';

import 'style/layout.css';
import 'style/split-pane.css';

interface MainProps {
  page: 'master' | 'puzzle';
  data: Model.Data;
  slug?: string;
}

const isBlank = x => x === undefined || x === null;

export const Main : React.FC<MainProps> = props => {
  const [slug, setSlug] = useState(props.page === 'puzzle' ? props.slug : undefined);
  const page = isBlank(slug) ? 'master' : 'puzzle';
  const [data, dataDispatch] = useReducer(Model.dataReducer, props.data);
  const iframeDetailsReducer = (state, action) => Object.assign({}, state, action);
  const [iframeDetails, iframeDetailsDispatch] = useReducer(iframeDetailsReducer, {});

  const [tabs, setTabs] = useLocalStorage<string[]>('main/puzzle-tabs', []);
  const [vsplitter, setVsplitter] = useLocalStorage<number>('frames/vsplitter', null);
  const [rhsplitter, setRhsplitter] = useLocalStorage<number>('frames/rhsplitter', null);

  // detect which rows are on screen
  const mainPaneChildRef = useRef(null);
  const [masterYDims, dispatchMasterYDims] = useReducer((state, action) => {
    const scrollTop = mainPaneChildRef.current.parentElement.scrollTop;
    const height = mainPaneChildRef.current.parentElement.getBoundingClientRect().height;
    const scrollHeight = mainPaneChildRef.current.parentElement.scrollHeight;
    const thresh = 0.1;
    if (state.scrollHeight === null ||
        Math.abs(scrollTop - state.scrollTop) >= thresh * height ||
        Math.abs((scrollTop + height) - (state.scrollTop + state.height)) >= thresh * height) {
      return {scrollTop, height, scrollHeight};
    } else {
      return state;
    }
  },
  {
    scrollTop: 0,
    height: document.body.getBoundingClientRect().height,
    scrollHeight: null,
  });
  useEffect(() => {
    const handler = () => {
      window.requestAnimationFrame(dispatchMasterYDims);
    }
    mainPaneChildRef.current.parentElement.addEventListener('scroll', handler, {passive: true});
    window.addEventListener('resize', handler, {passive: true});
    handler();
    return () => {
      mainPaneChildRef.current.parentElement.removeEventListener('scroll', handler);
      window.removeEventListener('resize', handler);
    };
  }, []);

  const hideSolved = useLocalStorageObject<boolean>('master/hide-solved', false);

  // because tabs can update outside of this window
  const [tabIndex, setTabIndex] = useState(null);
  const [initialLoad, setInitialLoad] = useState(true);

  const [hasExtension, setHasExtension] = useState(false);

  const uid = data.uid;
  const siteCtx = data.hunt;
  const puzzles = data.puzzles;
  const puzzleData = puzzles[slug];

  const puzzlesRef = useRef(puzzles);
  const siteCtxRef = useRef(siteCtx);
  const iframeDetailsRef = useRef(iframeDetails);
  useEffect(() => { puzzlesRef.current = puzzles; }, [puzzles]);
  useEffect(() => { siteCtxRef.current = siteCtx; }, [siteCtx]);
  useEffect(() => { iframeDetailsRef.current = iframeDetails; }, [iframeDetails]);
  const loadDiscord = useCallback((_slug, frameId) => {
    // BigInt doesn't fit in JSON types
    const nullOrString = x => isBlank(x) ? null : x.toString();
    const e = new CustomEvent('load-discord', {detail: {
      frameId: frameId,
      serverId: nullOrString(siteCtxRef.current.discord_server_id),
      voiceChannelId: nullOrString(puzzlesRef.current[_slug]?.discord_voice_channel_id),
      textChannelId: nullOrString(puzzlesRef.current[_slug]?.discord_text_channel_id),
    }});
    window.dispatchEvent(e);
  }, []);

  // Check for extension
  useEffect(() => {
    const handler = (e) => setHasExtension(true);
    window.addEventListener('pong', handler);
    window.dispatchEvent(new Event('ping'));
    return () => window.removeEventListener('pong', handler);
  }, []);
  // Reload history
  useEffect(() => {
    const handler = (e) => setSlug(e.state.slug);
    window.addEventListener('popstate', handler);
    return () => window.removeEventListener('popstate', handler);
  }, []);
  // custom event for listening to url changes in iframes
  useEffect(() => {
    const handler = (e) => {
      if (e.detail.name === 'discord' && !('discord' in iframeDetailsRef.current)) {
        loadDiscord(slug, e.detail.frameId);
      }
      iframeDetailsDispatch({[e.detail.name]: e.detail});
    }
    window.addEventListener('loaded-subframe', handler);
    return () => window.removeEventListener('loaded-subframe', handler);
  }, []);

  const addTab = useCallback(_slug => {
    if (puzzlesRef.current[_slug]?.hidden === false) {
      const _tabIndex = tabs.indexOf(_slug);
      if (_tabIndex === -1) {
        setTabs([_slug, ...tabs]);
        return 0;
      } else {
        return _tabIndex;
      }
    }
    return null;
  }, [tabs]);
  const loadSlug = useCallback(_slug => {
    if (_slug !== slug) {
      const _tabIndex = addTab(_slug);
      setSlug(_slug);
      setTabIndex(_tabIndex);
      const url = isBlank(_slug) ? '/' : `/puzzles/${_slug}`;
      history.pushState({slug: _slug}, '', url);
      loadDiscord(_slug, iframeDetailsRef.current.discord?.frameId);
    }
  }, [slug, addTab]);

  useEffect(() => {
    if (slug) {
      document.title = puzzleData?.name ?? 'Checkmate';
    } else {
      document.title = 'Master';
    }
  }, [slug]);

  // validate slug in tabs
  useEffect(() => {
    if (initialLoad) return;
    if (isBlank(slug)) return;
    if (!tabs.includes(slug)) loadSlug(undefined);
  }, [tabs, slug]);
  useEffect(() => {
    addTab(slug);
    setInitialLoad(false);
  }, []);
  useEffect(() => {
    if (tabs.some(slug => data.puzzles[slug]?.hidden !== false)) {
      setTabs(tabs.filter(slug => data.puzzles[slug]?.hidden === false));
    }
  }, [tabs, data]);

  const activateTab = loadSlug;
  const removeTab = useCallback((_slug) => {
    if (tabs.includes(_slug)) {
      const newTabs = tabs.filter(x => x !== _slug);
      setTabs(newTabs);
    }
  }, [tabs]);

  // connect to websocket for updates
  const socketRef = useRef(null);
  const reconnectDelayRef = useRef<number>(1);
  const updateCacheRef = useRef(null);
  useEffect(() => {
    const closeWebsocket = () => {
      try {
        socketRef.current.close();
      } catch (error) {}
    };
    const openWebsocket = () => {
      const socket = new WebSocket(`wss://${window.location.host}/ws/`);
      socket.addEventListener('message', (e) => {
        const _data = JSONbig.parse(e.data);
        dataDispatch({
          ws: socket,
          cacheRef: updateCacheRef,
          update: _data,
        });
      });
      socket.addEventListener('open', (e) => {
        reconnectDelayRef.current = 1;
      });
      socket.addEventListener('close', (e) => {
        setTimeout(openWebsocket, reconnectDelayRef.current * 1000);
        reconnectDelayRef.current += 1;
      });
      closeWebsocket();
      socketRef.current = socket;
    };
    openWebsocket();
    return closeWebsocket;
  }, []);

  const [initialDiscordUrl] = useState(Model.discordLink(
    siteCtx?.discord_server_id, puzzleData?.discord_text_channel_id));

  const [resizingClass, setResizingClass] = useState('');
  const onDragStarted = useCallback(() => setResizingClass('resizing'), []);
  const onDragFinishedSet = useCallback((set) => (x) => {
    setResizingClass('');
    return set(x);
  }, []);
  const onDragFinishedVsplitter = onDragFinishedSet(setVsplitter);
  const onDragFinishedRhsplitter = onDragFinishedSet(setRhsplitter);

  // TODO: extend with colors from database
  const statuses = baseStatuses;
  const colors = baseColors;

  return (
    <Base>
      <div className={`root vflex ${resizingClass} page-${page}`}>
        <TabBar {...{
          tabs,
          slug,
          activateTab,
          removeTab,
          siteCtx,
          puzzles,
          uid,
          colors,
        }}/>
        <div className='flex'>
          <SplitPane
            split='vertical'
            primary='second'
            defaultSize={vsplitter || 240}
            minSize={50}
            onDragStarted={onDragStarted}
            onDragFinished={onDragFinishedVsplitter}
          >
            <div ref={mainPaneChildRef}>
              <ShowIf display={page === 'master'}>
                <Master
                  isActive={page === 'master'}
                  data={data}
                  loadSlug={loadSlug}
                  statuses={statuses}
                  colors={colors}
                  hideSolved={hideSolved.value}
                  yDims={masterYDims}
                />
              </ShowIf>
              <ShowIf display={page === 'puzzle'}>
                <Puzzles
                  isActive={page === 'puzzle'}
                  tabs={tabs}
                  slug={slug}
                  puzzles={puzzles}
                  siteCtx={siteCtx}
                  iframeDetails={iframeDetails}
                  onDragStarted={onDragStarted}
                  onDragFinishedSet={onDragFinishedSet}
                />
              </ShowIf>
            </div>
            <SplitPane
              split='horizontal'
              defaultSize={rhsplitter || window.innerHeight / 2}
              onDragStarted={onDragStarted}
              onDragFinished={onDragFinishedRhsplitter}
            >
              <div className={`${page}info infopane pane`}>
                <ShowIf display={page === 'master'}>
                  <MasterInfo
                    data={data}
                    hideSolved={hideSolved}
                  />
                </ShowIf>
                <ShowIf display={page === 'puzzle'}>
                  <PuzzleInfo
                    data={data}
                    slug={slug}
                    loadSlug={loadSlug}
                    statuses={statuses}
                    colors={colors}
                  />
                </ShowIf>
              </div>
              <div className='chat pane'>
                <DiscordFrame
                  id='discord'
                  src={initialDiscordUrl}
                  hasExtension={hasExtension}
                />
              </div>
            </SplitPane>
          </SplitPane>
        </div>
      </div>
    </Base>
  );
};

export default mountElement(Main);
