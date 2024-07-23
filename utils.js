require('dotenv').config()

const moment = require('moment') // for date handling
const ical = require('node-ical'); // for ical parsing

const TBD_LOCATION_UID = process.env.TBD_LOCATION_UID 

// Do stuff with ical and GoogleAgenda
const pullUpcomingGaEvents = async (gAgendaPrivateUrlAd) => {
  const upcomingGaEvents = [];
  const data = await ical.fromURL(gAgendaPrivateUrlAd);
  // console.log("data - ", data);
  // Turn data object into an Array to filter based on value.type
  const dataAsArray = Object.entries(data);

  // Get the vCalendar metadata - used to enrich uid-externe
  const vCalendar = data.vcalendar;

  // // [NOT USED] Get the timezone
  // const timezoneFilter = dataAsArray.filter(([key, value]) => value.type === "VTIMEZONE");
  // const timezone = Object.fromEntries(timezoneFilter);

  // Get the actual event
  const eventsFilter = dataAsArray.filter(([key, value]) => {
    return (
      value.type === "VEVENT" &&
      moment(value.end).isAfter(moment())

    )
  });
  const events = Object.fromEntries(eventsFilter);

  for (const eventKey in events) {
    const gaEvent = data[eventKey];
    // Check if start and end are more than 24 h
    const timings = []
    if (moment(gaEvent.end).diff(moment(gaEvent.start), 'hours') < 24) {
      timings.push({
        begin: moment(gaEvent.start).toISOString(),
        end: moment(gaEvent.end).toISOString()
      })
    } else {
      // Split into an array of items that are maximum 24h
      let begin = moment(gaEvent.start)
      let end = moment(gaEvent.end)
      while (begin.isBefore(end)) {
        timings.push({
          begin: begin.toISOString(),
          end: begin.add(24, 'hours').toISOString()
        })
        begin = begin.add(24, 'hours')
      }
    }

    const newOaEvent = {
      "uid-externe": gaEvent.uid,
      slug: slugify(gaEvent.summary),
      title: { fr: gaEvent.summary },
      description: { fr: gaEvent.description ?? "-" },
      locationUid: TBD_LOCATION_UID,
      longDescription: { fr: `${gaEvent.location}\nImporté depuis ${vCalendar['WR-CALNAME']}` },
      timings
    }
    upcomingGaEvents.push(newOaEvent);
  }
  return upcomingGaEvents
}

const createOaEvent = async (oa, AGENDA_UID, event) => {
  return await oa.events.create(AGENDA_UID, event);
}

const updateOaEvent = async (oa, AGENDA_UID, eventUid, event) => {
  return await oa.events.update(AGENDA_UID, eventUid, event);
}

const patchOaEvent = async (oa, AGENDA_UID, eventUid, patch) => {
  return await oa.events.patch(AGENDA_UID, eventUid, patch);
}

const deleteOaEvents = async (oa, AGENDA_UID, uids) => {
  for (const uid of uids) {
    await oa.events.delete(AGENDA_UID, uid);
  }
  return uids
}

const slugify = text =>
  text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')

module.exports = { pullUpcomingGaEvents, createOaEvent, updateOaEvent, patchOaEvent, deleteOaEvents, slugify }